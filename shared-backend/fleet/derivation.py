"""Derivation engine.

Turns each raw telemetry point into higher-level state: trips, overspeed /
geofence / tamper / fuel / idle alerts, and live vehicle status. Runs
synchronously on every ingest (cheap at pilot scale; extractable to Celery later).

Everything is guarded for missing/None fields — the firmware is permissive and a
point may have no GPS fix, no speed, etc.

Fuel fill/theft rules are wired up but stay effectively inert while the flow
sensor reports 0 (see project notes) — the delta they watch for looks identical
to sensor noise without flow corroboration. Low fuel (absolute level, not a
delta) and excessive idle don't need that gate and are live once a company sets
a threshold (low_fuel_litres) / uses the idle default (max_idle_minutes).
"""

from django.conf import settings as dj_settings
from django.utils import timezone

from alerts.models import Alert
from alerts.services import raise_alert

from .geo import haversine_km, point_in_geofence
from .models import Geofence, GeofenceEvent, Telemetry, Trip

MOVING_KMPH = 3.0  # below this the truck is considered stopped
MAX_PLAUSIBLE_KMPH = 140  # segment-implied speed above this = GPS jitter, not real travel


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
        self.max_idle_minutes = cs.max_idle_minutes if cs else d["max_idle_minutes"]


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
        _handle_low_fuel(company, vehicle, device, t, prev, th)
        _handle_long_idle(company, vehicle, device, t, prev, th)
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
                pilot=vehicle.active_pilot,
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
    # A parked truck's GPS fix still drifts a few metres between reads; summed over many
    # pings that drift becomes many "phantom" kilometres (observed live: 12km accrued for
    # a vehicle whose own speed readings never exceeded 1.5 km/h). Require the device's own
    # speedometer to agree the truck was actually moving before trusting the GPS delta, and
    # separately cap any single segment's implied speed to drop one-off bad fixes — together
    # these keep distance_km (and therefore avg_speed_kmph) consistent with max_speed_kmph.
    moving = max(t.speed_kmph or 0, (prev.speed_kmph if prev else 0) or 0) > MOVING_KMPH
    if t.has_gps_fix and prev is not None and prev.has_gps_fix and moving:
        seg_km = haversine_km(prev.latitude, prev.longitude, t.latitude, t.longitude)
        elapsed_h = (t.received_at - prev.received_at).total_seconds() / 3600
        implied_kmph = (seg_km / elapsed_h) if elapsed_h > 0 else 0
        if implied_kmph <= MAX_PLAUSIBLE_KMPH:
            trip.distance_km += seg_km
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
    elapsed_min = (t.received_at - prev.received_at).total_seconds() / 60
    if elapsed_min <= 0:
        return
    delta = t.total_litres - prev.total_litres
    # A real fill/theft event must be corroborated by the flow sensor itself reporting
    # nonzero flow across the window. flow_rate_lpm reads 0 in every pilot record so far
    # (see PHASE1_SPEC) while total_litres still drifts/resets from sensor noise — without
    # this gate that noise was firing false fuel_fill/fuel_theft alerts. Once the flow
    # sensor genuinely reports nonzero flow, this gate opens automatically.
    observed_flow_lpm = max(t.flow_rate_lpm or 0, prev.flow_rate_lpm or 0)
    plausible_litres = observed_flow_lpm * elapsed_min
    if abs(delta) > max(plausible_litres * 2, 0.05):
        return
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


# --- low fuel (absolute level, no flow-sensor gate needed) --------------
def _handle_low_fuel(company, vehicle, device, t, prev, th):
    if th.low_fuel is None or t.total_litres is None or t.total_litres > th.low_fuel:
        return
    # rising edge only: fire once when crossing the threshold, not on every point after
    prev_above = prev is None or prev.total_litres is None or prev.total_litres > th.low_fuel
    if not prev_above:
        return
    raise_alert(
        company, type=Alert.Type.LOW_FUEL, severity=Alert.Severity.WARNING,
        title=f"Low fuel: {t.total_litres:.1f} L",
        message=f"{vehicle.registration_number} is down to {t.total_litres:.1f} L.",
        vehicle=vehicle, device=device,
        meta={"total_litres": t.total_litres, "threshold": th.low_fuel},
    )


# --- excessive idle ("too long waiting") ---------------------------------
def _handle_long_idle(company, vehicle, device, t, prev, th):
    if t.speed_kmph is None or t.speed_kmph > MOVING_KMPH:
        return
    last_moving = (
        Telemetry.objects.filter(vehicle=vehicle, speed_kmph__gt=MOVING_KMPH)
        .order_by("-received_at", "-pk")
        .first()
    )
    since = last_moving.received_at if last_moving else vehicle.created_at
    idle_minutes = (t.received_at - since).total_seconds() / 60
    if idle_minutes < th.max_idle_minutes:
        return
    # rising edge only: one alert per idle stretch, not one per point while it continues
    prev_idle_minutes = (prev.received_at - since).total_seconds() / 60 if prev else 0
    if prev_idle_minutes >= th.max_idle_minutes:
        return
    raise_alert(
        company, type=Alert.Type.IDLE_TOO_LONG, severity=Alert.Severity.WARNING,
        title=f"Idle {int(idle_minutes)} min",
        message=f"{vehicle.registration_number} has not moved for {int(idle_minutes)} minutes.",
        vehicle=vehicle, device=device,
        lat=t.latitude if t.has_gps_fix else None,
        lng=t.longitude if t.has_gps_fix else None,
        meta={"idle_minutes": int(idle_minutes)},
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
                # A trip normally only closes when a *new* telemetry point reveals the
                # gap; a device that goes silent for good would otherwise leave its
                # last trip "active" forever. Close it here using the last known point.
                active_trip = (
                    Trip.objects.filter(vehicle=vehicle, status=Trip.Status.ACTIVE)
                    .order_by("-started_at")
                    .first()
                )
                if active_trip:
                    last_point = (
                        Telemetry.objects.filter(vehicle=vehicle)
                        .order_by("-received_at", "-pk")
                        .first()
                    )
                    if last_point:
                        _close_trip(active_trip, last_point)
            raise_alert(
                company, type=Alert.Type.DEVICE_OFFLINE, severity=Alert.Severity.WARNING,
                title="Device offline",
                message=f"{device.device_id} has not reported for {int(silent)}s.",
                vehicle=vehicle, device=device, meta={"silent_seconds": int(silent)},
            )
    return newly
