"""Role-based permissions and company scoping.

Every Owner-facing endpoint is scoped to request.user.company. Super-admins see
everything. Drivers get their own narrow scope (fleshed out in Phase 2).
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission

from core.models import User


class CanWriteOrReadOnly(BasePermission):
    """Everyone authorized may READ; only Super Admin or an admin-granted
    `can_edit` user may WRITE (create/update/delete + mutating actions).

    Combine with a role/scope permission (e.g. IsOwnerOrAdmin) — DRF ANDs them,
    so the role gate still decides *who can see the endpoint at all*, while this
    decides *who may change things*.
    """

    message = "Editing is disabled for your account. Ask an administrator to enable it."

    def has_permission(self, request, view):
        u = request.user
        if not (u and u.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return bool(getattr(u, "may_write", False))


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == User.Role.SUPERADMIN)


class IsOwnerOrAdmin(BasePermission):
    """Owner / Manager of a company, or a platform super-admin."""

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and (
            u.role in (User.Role.OWNER, User.Role.MANAGER, User.Role.SUPERADMIN)
        ))


class IsDriver(BasePermission):
    """A driver account. Sees only their own assigned vehicle's data."""

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.role == User.Role.DRIVER)


class CompanyScopedQuerysetMixin:
    """Filter a viewset's queryset to the caller's company.

    Super-admins are unrestricted. Non-superadmin users with no company see
    nothing (safer than leaking). `company_field` says how to reach Company from
    the model (default 'company'); use e.g. 'vehicle__company' for nested models.
    """

    company_field = "company"

    def scoped(self, queryset):
        u = self.request.user
        if u.role == User.Role.SUPERADMIN:
            return queryset
        if not u.company_id:
            return queryset.none()
        return queryset.filter(**{self.company_field: u.company_id})
