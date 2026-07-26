"""Tenancy, users, and per-company settings.

Company is the tenant: every business row in the system FKs (directly or via a
vehicle/device) back to a Company, and every Owner-scoped API query is filtered
to request.user.company. This is what lets 5 or 30 trucks across 1..N companies
be pure data, not code changes.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Company(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom user set from line 1 (AUTH_USER_MODEL) — cannot be swapped later.

    A SUPERADMIN has no company (platform-wide). Everyone else belongs to one.
    """

    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "Super Admin"
        OWNER = "owner", "Owner"
        MANAGER = "manager", "Manager"
        DRIVER = "driver", "Driver"

    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.CASCADE, related_name="users"
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.OWNER)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class CompanySettings(models.Model):
    """Per-company thresholds for the derivation engine. Falls back to
    settings.DERIVATION_DEFAULTS when a row does not exist."""

    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="settings")
    overspeed_limit_kmph = models.PositiveIntegerField(default=60)
    offline_after_seconds = models.PositiveIntegerField(default=900)
    low_fuel_litres = models.FloatField(null=True, blank=True)
    theft_drop_litres = models.FloatField(default=5)
    tamper_on_lock_change = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "company settings"

    def __str__(self):
        return f"settings: {self.company}"
