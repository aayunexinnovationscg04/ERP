"""Command queue — server-to-device messages delivered on the device's next POST.

Replaces the old queues.json. The device is behind carrier NAT and can never be
reached directly, so commands ride back in the reply to the device's own POST.
"""

from django.db import models

from fleet.models import Device


class Command(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        DELIVERED = "delivered", "Delivered"

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="commands")
    payload = models.CharField(max_length=60)           # e.g. "open", "testing"
    content_type = models.CharField(max_length=60, default="text/plain")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["device", "status"])]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.payload} -> {self.device} ({self.status})"
