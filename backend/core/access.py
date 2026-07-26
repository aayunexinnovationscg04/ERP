"""Resolve a user's effective module access.

Precedence:  per-user override  >  role default (RolePermission)  >  False.
Super Admin is always all-access (cannot be locked out of the platform).
"""

from .models import RolePermission, User, UserModuleOverride
from .modules import MODULE_KEYS


def role_defaults(role):
    """{module: allowed} for a role, from RolePermission (missing => False)."""
    rows = {rp.module: rp.allowed for rp in RolePermission.objects.filter(role=role)}
    return {m: rows.get(m, False) for m in MODULE_KEYS}


def effective_modules(user):
    """List of module keys the user may access."""
    if not user or not user.is_authenticated:
        return []
    if user.role == User.Role.SUPERADMIN:
        return list(MODULE_KEYS)
    base = role_defaults(user.role)
    for ov in UserModuleOverride.objects.filter(user=user):
        if ov.module in base:
            base[ov.module] = ov.allowed
    return [m for m, ok in base.items() if ok]


def role_matrix():
    """Full {role: {module: allowed}} matrix for the Role Management screen."""
    out = {}
    for role, _ in User.Role.choices:
        if role == User.Role.SUPERADMIN:
            out[role] = {m: True for m in MODULE_KEYS}  # informational, all-access
        else:
            out[role] = role_defaults(role)
    return out
