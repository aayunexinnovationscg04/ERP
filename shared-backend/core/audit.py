"""Audit trail: every action a dealer, manager or pilot account takes.

Views call `record(...)` for the actions they understand (with a readable summary
and before/after `changes`); `AuditMiddleware` then catches any other successful
write by those roles that no view recorded, so nothing slips through when a new
endpoint is added. The admin Audit Logs screen reads `AuditLog`.
"""

import logging

from django.db import DatabaseError
from django.forms.models import model_to_dict

log = logging.getLogger("fuelguardx.audit")

AUDITED_ROLES = {"dealer", "manager", "pilot"}
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
# auth endpoints record themselves (with the user resolved from the credentials)
SELF_RECORDING_PREFIXES = ("/api/auth/",)
# never store these, even inside a change set
SECRET_FIELDS = {"password", "token", "ticket", "access", "refresh"}


def client_ip(request):
    # Caddy -> nginx -> gunicorn: the first X-Forwarded-For hop is the client.
    fwd = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = fwd.split(",")[0].strip() if fwd else request.META.get("REMOTE_ADDR", "")
    return ip or None


def _plain(v):
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return str(v)


def snapshot(obj, fields=None):
    """Plain dict of a model instance's field values (for before/after diffs)."""
    data = model_to_dict(obj, fields=fields)
    return {k: _plain(v) for k, v in data.items() if k not in SECRET_FIELDS}


def diff(before, after):
    """{field: [before, after]} for the fields that changed."""
    keys = set(before) | set(after)
    return {k: [before.get(k), after.get(k)] for k in sorted(keys)
            if k not in SECRET_FIELDS and before.get(k) != after.get(k)}


def record(request, action, summary, *, user=None, target=None, target_type="", target_id="", target_label="",
           changes=None, ok=True, portal=""):
    """Write one audit row. Never raises: auditing must not break the action itself."""
    from .models import AuditLog

    u = user if user is not None else getattr(request, "user", None)
    if u is not None and not getattr(u, "is_authenticated", False):
        u = None
    try:
        company = getattr(u, "company", None) if u else None
        AuditLog.objects.create(
            actor=u,
            actor_username=getattr(u, "username", "") or "",
            actor_role=getattr(u, "role", "") or "",
            company=company,
            company_name=getattr(company, "name", "") or "",
            action=action,
            summary=summary[:300],
            target_type=target_type or (target._meta.model_name if target is not None else ""),
            target_id=str(target_id or (getattr(target, "pk", "") if target is not None else "") or ""),
            target_label=(target_label or (str(target) if target is not None else ""))[:200],
            changes={k: v for k, v in (changes or {}).items() if k not in SECRET_FIELDS},
            ok=ok,
            portal=portal or request.META.get("HTTP_X_FGX_PORTAL", "")[:10],
            ip=client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
            method=request.method,
            path=request.path[:300],
        )
    except DatabaseError:
        log.exception("audit write failed: %s %s", action, summary)
    # tell the middleware this request is already accounted for
    setattr(getattr(request, "_request", request), "_fgx_audited", True)


class AuditMiddleware:
    """Catch-all: log any successful write by a dealer/manager/pilot that no view
    recorded explicitly (e.g. an endpoint added later)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            u = getattr(request, "user", None)
            if (request.method not in SAFE_METHODS
                    and request.path.startswith("/api/")
                    and not request.path.startswith(SELF_RECORDING_PREFIXES)
                    and response.status_code < 400
                    and not getattr(request, "_fgx_audited", False)
                    and u is not None and getattr(u, "is_authenticated", False)
                    and getattr(u, "role", "") in AUDITED_ROLES):
                record(request, f"api.{request.method.lower()}",
                       f"{request.method} {request.path}", user=u)
        except Exception:  # auditing must never break a response
            log.exception("audit middleware failed")
        return response
