"""Fleet domain: devices, vehicles, drivers, telemetry, trips, geofences.

Telemetry is the high-volume table (every device POST lands here). It keeps
both typed columns (for querying/aggregation) and the full raw payload (JSONB),
so nothing the firmware sends is ever lost even if the schema drifts.
"""

from django.db import models

from core.models import Company


class Device(models.Model):
    """An ESP32 + SIM800L unit. Identified by device_id (e.g. 'esp32-01')."""

    device_id = models.CharField(max_length=100, unique=True)
    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.SET_NULL, related_name="devices"
    )
    label = models.CharField(max_length=120, blank=True)
    sim_number = models.CharField(max_length=20, blank=True)
    firmware_version = models.CharField(max_length=40, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    last_ip = models.CharField(max_length=64, blank=True)
    online = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.device_id


class Driver(models.Model):
    """Minimal in Phase 1 (identity + assignment). Attendance/salary land in P2."""

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="drivers")
    user = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="driver_profiles"
    )
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    license_no = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        IDLE = "idle", "Idle"
        OFFLINE = "offline", "Offline"
        MAINTENANCE = "maintenance", "Maintenance"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="vehicles")
    registration_number = models.CharField(max_length=40)
    make = models.CharField(max_length=60, blank=True)
    model = models.CharField(max_length=60, blank=True)
    tank_capacity_litres = models.FloatField(null=True, blank=True)
    device = models.OneToOneField(
        Device, null=True, blank=True, on_delete=models.SET_NULL, related_name="vehicle"
    )
    active_driver = models.ForeignKey(
        Driver, null=True, blank=True, on_delete=models.SET_NULL, related_name="vehicles"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OFFLINE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "registration_number"], name="uniq_reg_per_company"
            )
        ]

    def __str__(self):
        return self.registration_number


class Telemetry(models.Model):
    """One row per device POST. Typed columns + raw JSONB fallback."""

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="telemetry")
    vehicle = models.ForeignKey(
        Vehicle, null=True, blank=True, on_delete=models.SET_NULL, related_name="telemetry"
    )
    device_ts = models.DateTimeField(null=True, blank=True)   # device clock, if sent
    received_at = models.DateTimeField(auto_now_add=True)     # server clock (authoritative)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    speed_kmph = models.FloatField(null=True, blank=True)
    satellites = models.IntegerField(null=True, blank=True)
    altitude_m = models.FloatField(null=True, blank=True)
    flow_rate_lpm = models.FloatField(null=True, blank=True)
    total_litres = models.FloatField(null=True, blank=True)
    recording = models.BooleanField(null=True, blank=True)
    lock_active = models.BooleanField(null=True, blank=True)
    gsm_signal = models.IntegerField(null=True, blank=True)

    has_gps_fix = models.BooleanField(default=False)
    raw = models.JSONField(default=dict, blank=True)          # full payload, never lost

    class Meta:
        indexes = [
            models.Index(fields=["device", "received_at"]),
            models.Index(fields=["vehicle", "received_at"]),
        ]
        ordering = ["-received_at"]

    def __str__(self):
        return f"{self.device.device_id} @ {self.received_at:%Y-%m-%d %H:%M:%S}"


class Trip(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="trips")
    driver = models.ForeignKey(
        Driver, null=True, blank=True, on_delete=models.SET_NULL, related_name="trips"
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    start_lat = models.FloatField(null=True, blank=True)
    start_lng = models.FloatField(null=True, blank=True)
    end_lat = models.FloatField(null=True, blank=True)
    end_lng = models.FloatField(null=True, blank=True)
    distance_km = models.FloatField(default=0)
    max_speed_kmph = models.FloatField(default=0)
    avg_speed_kmph = models.FloatField(default=0)
    fuel_consumed_litres = models.FloatField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        indexes = [models.Index(fields=["vehicle", "status", "started_at"])]
        ordering = ["-started_at"]

    def __str__(self):
        return f"trip {self.pk} · {self.vehicle}"


class Geofence(models.Model):
    class Kind(models.TextChoices):
        CIRCLE = "circle", "Circle"
        POLYGON = "polygon", "Polygon"

    class Purpose(models.TextChoices):
        ALLOWED = "allowed", "Allowed zone"
        RESTRICTED = "restricted", "Restricted zone"
        CUSTOMER_SITE = "customer_site", "Customer site"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="geofences")
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.CIRCLE)
    center_lat = models.FloatField(null=True, blank=True)
    center_lng = models.FloatField(null=True, blank=True)
    radius_m = models.FloatField(null=True, blank=True)
    polygon = models.JSONField(null=True, blank=True)  # [[lat,lng], ...] for polygons
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.ALLOWED)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GeofenceEvent(models.Model):
    class Event(models.TextChoices):
        ENTER = "enter", "Enter"
        EXIT = "exit", "Exit"

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="geofence_events")
    geofence = models.ForeignKey(Geofence, on_delete=models.CASCADE, related_name="events")
    event = models.CharField(max_length=10, choices=Event.choices)
    ts = models.DateTimeField()
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-ts"]

    def __str__(self):
        return f"{self.vehicle} {self.event} {self.geofence}"
