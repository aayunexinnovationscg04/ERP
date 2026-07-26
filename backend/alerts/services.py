"""Helper to raise alerts from the derivation engine."""

from .models import Alert


def raise_alert(company, *, type, severity=Alert.Severity.WARNING, title, message="",
                vehicle=None, device=None, lat=None, lng=None, meta=None):
    """Create an Alert. `company` is required (multi-tenant scoping).

    Returns the created Alert, or None if no company could be resolved (e.g. a
    device not yet assigned to a company — we don't want orphan alerts)."""
    if company is None:
        return None
    return Alert.objects.create(
        company=company,
        vehicle=vehicle,
        device=device,
        type=type,
        severity=severity,
        title=title,
        message=message,
        lat=lat,
        lng=lng,
        meta=meta or {},
    )
