"""Fleet domain: devices, vehicles, pilots, telemetry, trips, geofences.

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


class Pilot(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="pilots")
    user = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="pilot_profiles"
    )
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    license_no = models.CharField(max_length=40, blank=True)
    # Entered via Django Admin (no self-service payroll UI) — same pattern as
    # VehicleDocument: admin-entered, frontend read-only.
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PilotAttendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        HALF_DAY = "half_day", "Half day"
        LEAVE = "leave", "On leave"

    pilot = models.ForeignKey(Pilot, on_delete=models.CASCADE, related_name="attendance")
    date = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["pilot", "date"], name="uniq_attendance_per_day")
        ]
        ordering = ["-date"]
        verbose_name_plural = "pilot attendance"

    def __str__(self):
        return f"{self.pilot} · {self.date} · {self.status}"


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
    active_pilot = models.ForeignKey(
        Pilot, null=True, blank=True, on_delete=models.SET_NULL, related_name="vehicles"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OFFLINE)
    # Dealer-facing nickname, separate from the (often cryptic) registration
    # number — e.g. "Loader 2". Editable anytime by the dealer/admin.
    local_name = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "registration_number"], name="uniq_reg_per_company"
            )
        ]

    def save(self, *args, **kwargs):
        if not self.local_name:
            n = Vehicle.objects.filter(company_id=self.company_id).count() + 1
            self.local_name = f"Vehicle {n}"[:10]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.registration_number


class VehicleDocument(models.Model):
    class DocType(models.TextChoices):
        RC = "rc", "Registration (RC)"
        INSURANCE = "insurance", "Insurance"
        PERMIT = "permit", "Permit"
        PUC = "puc", "Pollution (PUC)"
        FITNESS = "fitness", "Fitness certificate"
        OTHER = "other", "Other"

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    number = models.CharField(max_length=80, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [models.F("expiry_date").asc(nulls_last=True)]

    def __str__(self):
        return f"{self.vehicle} · {self.get_doc_type_display()}"


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
    pilot = models.ForeignKey(
        Pilot, null=True, blank=True, on_delete=models.SET_NULL, related_name="trips"
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
