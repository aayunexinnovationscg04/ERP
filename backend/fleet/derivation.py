"""Derivation engine.

Turns each raw telemetry point into higher-level state: trips, overspeed /
geofence / tamper / fuel alerts, and live vehicle status. Runs synchronously on
every ingest (cheap at pilot scale; extractable to Celery later).

Everything is guarded for missing/None fields — the firmware is permissive and a
point may have no GPS fix, no speed, etc.

Fuel rules (fill / theft / low) are wired up but stay effectively inert while the
flow sensor reports 0 (see project notes).
"""

from django.conf import settings as dj_settings
from django.utils import timezone

from alerts.models import Alert
from alerts.services import raise_alert

from .geo import haversine_km, point_in_geofence
from .models import Geofence, GeofenceEvent, Telemetry, Trip

MOVING_KMPH = 3.0  # below this the truck is considered stopped


class _Thresholds:
    """Per-company settings with fallback to project defaults."""

    def __init__(self, company):
        d = dj_settings.DERIVATION_DEFAULTS
        cs = getattr(company, "settings", None) if company else None
        self.overspeed = cs.overspeed_limit_kmph if cs else d["overspeed_limit_kmph"]
        self.offline_after = cs.offline_after_seconds if cs else d["offline_after_seconds"]
        self.low_fuel = cs.low_fuel_litres if cs else None
        self.theft_drop = cs.theft_drop_litres if cs else d["theft_drop_litres"]
        self.tamper_on_lock_change = cs.tamper_on_lock_change if cs else True


def _prev(t):
    return (
        Telemetry.objects.filter(device=t.device, received_at__lte=t.received_at)
        .exclude(pk=t.pk)
        .order_by("-received_at", "-pk")
        .first()
    )


def process_telemetry(t):
    """Main entry point. `t` is a freshly-saved Telemetry row."""
    device = t.device
    vehicle = t.vehicle or getattr(device, "vehicle", None)
    company = (vehicle.company if vehicle else None) or device.company
    th = _Thresholds(company)
    prev = _prev(t)

    _update_device(device, t)
    if vehicle:
        _handle_trip(vehicle, t, prev, th)
        _handle_overspeed(company, vehicle, device, t, prev, th)
        _handle_geofence(company, vehicle, t, prev)
        _handle_tamper(company, vehicle, device, t, prev, th)
        _handle_fuel(company, vehicle, device, t, prev, th)
        _update_vehicle_status(vehicle, t)


# --- device -------------------------------------------------------------
def _update_device(device, t):
    device.last_seen = t.received_at
    if t.raw.get("_client_ip"):
        device.last_ip = t.raw["_client_ip"]
    device.online = True
    device.save(update_fields=["last_seen", "last_ip", "online"])


# --- trips --------------------------------------------------------------
def _handle_trip(vehicle, t, prev, th):
    active = Trip.objects.filter(vehicle=vehicle, status=Trip.Status.ACTIVE).order_by("-started_at").first()

    # A long gap since the previous point means the old trip is stale — close it.
    if active and prev:
        gap = (t.received_at - prev.received_at).total_seconds()
        if gap > th.offline_after:
            _close_trip(active, prev)
            active = None

    recording = bool(t.recording)
    if recording:
        if active is None:
            active = Trip.objects.create(
                vehicle=vehicle,
                driver=vehicle.active_driver,
                started_at=t.received_at,
                start_lat=t.latitude if t.has_gps_fix else None,
                start_lng=t.longitude if t.has_gps_fix else None,
                status=Trip.Status.ACTIVE,
            )
        _accumulate_trip(active, t, prev)
    else:
        if active is not None:
            _close_trip(active, t)


def _accumulate_trip(trip, t, prev):
    """Grow distance / max-speed / fuel as points arrive. Average speed is derived
    at close time from distance and duration (persistent and simple)."""
    fields = []
    if t.has_gps_fix and prev is not None and prev.has_gps_fix:
        trip.distance_km += haversine_km(prev.latitude, prev.longitude, t.latitude, t.longitude)
        fields.append("distance_km")
    if t.speed_kmph is not None and t.speed_kmph > trip.max_speed_kmph:
        trip.max_speed_kmph = t.speed_kmph
        fields.append("max_speed_kmph")
    if t.total_litres is not None and prev is not None and prev.total_litres is not None:
        delta = t.total_litres - prev.total_litres
        if delta > 0:
            trip.fuel_consumed_litres += delta
            fields.append("fuel_consumed_litres")
    if fields:
        trip.save(update_fields=list(set(fields)))


def _close_trip(trip, last):
    trip.status = Trip.Status.COMPLETED
    trip.ended_at = last.received_at
    if last.has_gps_fix:
        trip.end_lat = last.latitude
        trip.end_lng = last.longitude
    hours = (trip.ended_at - trip.started_at).total_seconds() / 3600 if trip.ended_at else 0
    trip.avg_speed_kmph = (trip.distance_km / hours) if hours > 0 else 0
    trip.save(update_fields=["status", "ended_at", "end_lat", "end_lng", "avg_speed_kmph"])


# --- overspeed ----------------------------------------------------------
def _handle_overspeed(company, vehicle, device, t, prev, th):
    if t.speed_kmph is None or t.speed_kmph <= th.overspeed:
        return
    # rising edge only: don't spam one alert per point in a continuous violation
    prev_over = prev is not None and prev.speed_kmph is not None and prev.speed_kmph > th.overspeed
    if prev_over:
        return
    raise_alert(
        company, type=Alert.Type.OVERSPEED, severity=Alert.Severity.WARNING,
        title=f"Overspeed: {t.speed_kmph:.0f} km/h",
        message=f"{vehicle.registration_number} exceeded {th.overspeed} km/h.",
        vehicle=vehicle, device=device,
        lat=t.latitude if t.has_gps_fix else None,
        lng=t.longitude if t.has_gps_fix else None,
        meta={"speed_kmph": t.speed_kmph, "limit": th.overspeed},
    )


# --- geofence -----------------------------------------------------------
def _handle_geofence(company, vehicle, t, prev):
    if not t.has_gps_fix or company is None:
        return
    fences = Geofence.objects.filter(company=company, active=True)
    for gf in fences:
        now_in = point_in_geofence(t.latitude, t.longitude, gf)
        was_in = bool(
            prev and prev.has_gps_fix and point_in_geofence(prev.latitude, prev.longitude, gf)
        )
        if now_in == was_in:
            continue
        event = GeofenceEvent.Event.ENTER if now_in else GeofenceEvent.Event.EXIT
        GeofenceEvent.objects.create(
            vehicle=vehicle, geofence=gf, event=event, ts=t.received_at,
            lat=t.latitude, lng=t.longitude,
        )
        # Alert on the meaningful direction per zone purpose.
        breach = (now_in and gf.purpose == Geofence.Purpose.RESTRICTED) or (
            not now_in and gf.purpose == Geofence.Purpose.ALLOWED
        )
        if breach:
            raise_alert(
                company, type=Alert.Type.GEOFENCE_BREACH, severity=Alert.Severity.WARNING,
                title=f"Geofence {event}: {gf.name}",
                message=f"{vehicle.registration_number} {event}ed {gf.get_purpose_display()} '{gf.name}'.",
                vehicle=vehicle, lat=t.latitude, lng=t.longitude,
                meta={"geofence": gf.name, "event": event, "purpose": gf.purpose},
            )


# --- tamper -------------------------------------------------------------
def _handle_tamper(company, vehicle, device, t, prev, th):
    if not th.tamper_on_lock_change or t.lock_active is None or prev is None or prev.lock_active is None:
        return
    # lock disengaged (True -> False) = fuel cap / lock opened
    if prev.lock_active and not t.lock_active:
        raise_alert(
            company, type=Alert.Type.TAMPER, severity=Alert.Severity.CRITICAL,
            title="Lock opened",
            message=f"{vehicle.registration_number}: fuel lock was opened.",
            vehicle=vehicle, device=device,
            lat=t.latitude if t.has_gps_fix else None,
            lng=t.longitude if t.has_gps_fix else None,
            meta={"lock_active": False},
        )


# --- fuel (inert until sensor reports non-zero) -------------------------
def _handle_fuel(company, vehicle, device, t, prev, th):
    if t.total_litres is None or prev is None or prev.total_litres is None:
        return
    delta = t.total_litres - prev.total_litres
    if delta >= 1.0:
        raise_alert(
            company, type=Alert.Type.FUEL_FILL, severity=Alert.Severity.INFO,
            title=f"Fuel fill: +{delta:.1f} L",
            message=f"{vehicle.registration_number} refuelled {delta:.1f} L.",
            vehicle=vehicle, device=device, meta={"delta_litres": delta},
        )
    elif delta <= -th.theft_drop:
        raise_alert(
            company, type=Alert.Type.FUEL_THEFT, severity=Alert.Severity.CRITICAL,
            title=f"Possible fuel theft: {delta:.1f} L",
            message=f"{vehicle.registration_number} lost {abs(delta):.1f} L suddenly.",
            vehicle=vehicle, device=device,
            lat=t.latitude if t.has_gps_fix else None,
            lng=t.longitude if t.has_gps_fix else None,
            meta={"delta_litres": delta},
        )


# --- vehicle live status ------------------------------------------------
def _update_vehicle_status(vehicle, t):
    if t.recording and t.speed_kmph is not None and t.speed_kmph > MOVING_KMPH:
        status = vehicle.Status.ACTIVE
    else:
        status = vehicle.Status.IDLE
    if vehicle.status != status:
        vehicle.status = status
        vehicle.save(update_fields=["status"])


def mark_offline(now=None):
    """Sweep: flag devices silent longer than their company's offline window, and
    raise a DEVICE_OFFLINE alert once per transition. Returns count newly offline."""
    now = now or timezone.now()
    from .models import Device  # local import to avoid cycles

    newly = 0
    for device in Device.objects.filter(online=True):
        vehicle = getattr(device, "vehicle", None)
        company = (vehicle.company if vehicle else None) or device.company
        th = _Thresholds(company)
        if not device.last_seen:
            continue
        silent = (now - device.last_seen).total_seconds()
        if silent > th.offline_after:
            device.online = False
            device.save(update_fields=["online"])
            newly += 1
            if vehicle:
                vehicle.status = vehicle.Status.OFFLINE
                vehicle.save(update_fields=["status"])
            raise_alert(
                company, type=Alert.Type.DEVICE_OFFLINE, severity=Alert.Severity.WARNING,
                title="Device offline",
                message=f"{device.device_id} has not reported for {int(silent)}s.",
                vehicle=vehicle, device=device, meta={"silent_seconds": int(silent)},
            )
    return newly
