"""Alerts produced by the derivation engine (overspeed, geofence, fuel, tamper,
device offline). Fuel-related types are wired up but stay inert until the flow
sensor reports non-zero values."""

from django.db import models

from core.models import Company
from fleet.models import Device, Vehicle


class Alert(models.Model):
    class Type(models.TextChoices):
        OVERSPEED = "overspeed", "Overspeed"
        GEOFENCE_BREACH = "geofence_breach", "Geofence breach"
        LOW_FUEL = "low_fuel", "Low fuel"
        FUEL_FILL = "fuel_fill", "Fuel fill"
        FUEL_THEFT = "fuel_theft", "Fuel theft"
        TAMPER = "tamper", "Tamper"
        DEVICE_OFFLINE = "device_offline", "Device offline"
        SENSOR_FAULT = "sensor_fault", "Sensor fault"

    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="alerts")
    vehicle = models.ForeignKey(
        Vehicle, null=True, blank=True, on_delete=models.SET_NULL, related_name="alerts"
    )
    device = models.ForeignKey(
        Device, null=True, blank=True, on_delete=models.SET_NULL, related_name="alerts"
    )
    type = models.CharField(max_length=30, choices=Type.choices)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.WARNING)
    title = models.CharField(max_length=160)
    message = models.TextField(blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_by = models.ForeignKey(
        "core.User", null=True, blank=True, on_delete=models.SET_NULL, related_name="acked_alerts"
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["company", "status", "created_at"])]
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.severity}] {self.type} · {self.vehicle or self.device}"
