"""Tenancy, users, and per-company settings.

Company is the tenant: every business row in the system FKs (directly or via a
vehicle/device) back to a Company, and every Dealer-scoped API query is filtered
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

    An ADMIN has no company (platform-wide). Everyone else belongs to one.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        DEALER = "dealer", "Dealer"
        MANAGER = "manager", "Manager"
        PILOT = "pilot", "Pilot"

    company = models.ForeignKey(
        Company, null=True, blank=True, on_delete=models.CASCADE, related_name="users"
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DEALER)
    phone = models.CharField(max_length=20, blank=True)
    # Legacy per-user write gate, no longer checked (see may_write). Kept so old
    # rows and API clients keep working.
    can_edit = models.BooleanField(
        default=False,
        help_text="If on, this user may make changes (create/edit/delete). "
                  "Admins can always edit regardless of this flag.",
    )
    # Embedded in every JWT as "sv". Bumping it (password/role/company/active
    # change, or "sign out everywhere") instantly invalidates all issued tokens.
    session_version = models.PositiveIntegerField(default=0, editable=False)

    @property
    def may_write(self):
        if self.role == self.Role.ADMIN:
            return True
        # Every dealer/manager/pilot has full permissions; only a suspended
        # company is read-only for everyone in it. (`can_edit` is no longer used.)
        return not (self.company_id and self.company.status == Company.Status.SUSPENDED)

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
    max_idle_minutes = models.PositiveIntegerField(
        default=45, help_text="Alert when a vehicle sits stopped (not moving) this long."
    )

    class Meta:
        verbose_name_plural = "company settings"

    def __str__(self):
        return f"settings: {self.company}"


class RolePermission(models.Model):
    """Global (platform-wide) default: does `role` get access to `module`?

    Managed by Admin via Role Management. One row per (role, module).
    Admin is always all-access and is not represented here.
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


class ViewAsTicket(models.Model):
    """One-time pass an admin uses to open a dealer/pilot portal as that user,
    view-only. Valid for 60 seconds and a single use (see core/tokens.py)."""

    jti = models.CharField(max_length=64, unique=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    portal = models.CharField(max_length=10)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"view-as {self.admin_id}->{self.target_id} ({self.portal})"


class AuditLog(models.Model):
    """One action taken by an account: sign-in/out, or any change it made.

    Written by core.audit.record() (explicit, with before/after changes) and by
    core.audit.AuditMiddleware (a catch-all for any other successful write), and
    read by the admin Audit Logs screen. Rows are never edited.
    """

    at = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="audit_logs")
    # copied at write time so the log still reads correctly if the account changes
    actor_username = models.CharField(max_length=150, blank=True)
    actor_role = models.CharField(max_length=20, blank=True, db_index=True)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    company_name = models.CharField(max_length=200, blank=True)
    action = models.CharField(max_length=60, db_index=True)   # e.g. "geofence.update"
    summary = models.CharField(max_length=300)                 # one readable line
    target_type = models.CharField(max_length=40, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    target_label = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict, blank=True)       # {field: [before, after]}
    ok = models.BooleanField(default=True)                     # False for e.g. a failed sign-in
    portal = models.CharField(max_length=10, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    method = models.CharField(max_length=8, blank=True)
    path = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ["-at", "-id"]
        indexes = [models.Index(fields=["actor", "-at"]), models.Index(fields=["actor_role", "-at"])]

    def __str__(self):
        return f"{self.at:%Y-%m-%d %H:%M} {self.actor_username} {self.action}"
