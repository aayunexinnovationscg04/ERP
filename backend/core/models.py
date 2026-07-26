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
    # Write gate: non-superadmins can VIEW their data but cannot CHANGE anything
    # unless a Super Admin grants this. Super Admin always has full write access.
    can_edit = models.BooleanField(
        default=False,
        help_text="If on, this user may make changes (create/edit/delete). "
                  "Super Admins can always edit regardless of this flag.",
    )

    @property
    def may_write(self):
        return self.role == self.Role.SUPERADMIN or self.can_edit

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


class RolePermission(models.Model):
    """Global (platform-wide) default: does `role` get access to `module`?

    Managed by Super Admin via Role Management. One row per (role, module).
    Super Admin is always all-access and is not represented here.
    """

    role = models.CharField(max_length=20, choices=User.Role.choices)
    module = models.CharField(max_length=40)
    allowed = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["role", "module"], name="uniq_role_module")
        ]

    def __str__(self):
        return f"{self.role}:{self.module}={self.allowed}"


class UserModuleOverride(models.Model):
    """Per-member override of a module's access, winning over the role default."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="module_overrides")
    module = models.CharField(max_length=40)
    allowed = models.BooleanField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "module"], name="uniq_user_module")
        ]

    def __str__(self):
        return f"{self.user_id}:{self.module}={self.allowed}"
