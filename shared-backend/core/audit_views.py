"""Admin: read the audit trail (GET /api/admin/audit)."""

from datetime import datetime, time

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import ListAPIView

from .models import AuditLog
from .permissions import IsAdmin

ROLE_GROUPS = {"dealer": ["dealer", "manager"], "pilot": ["pilot"]}


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ["id", "at", "actor", "actor_username", "actor_role", "company", "company_name",
                  "action", "summary", "target_type", "target_id", "target_label", "changes", "ok",
                  "portal", "ip", "user_agent", "method", "path"]


def _day(value, end=False):
    """'YYYY-MM-DD' or ISO datetime -> aware datetime (start or end of that day)."""
    try:
        if len(value) == 10:
            d = datetime.strptime(value, "%Y-%m-%d").date()
            return timezone.make_aware(datetime.combine(d, time.max if end else time.min))
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt if timezone.is_aware(dt) else timezone.make_aware(dt)
    except ValueError:
        return None


class AuditLogView(ListAPIView):
    """Filters: role=dealer|pilot, actor=<user id>, company=<id>,
    action=<prefix, e.g. geofence>, from/to=<date or ISO time>, q=<text>."""

    permission_classes = [IsAdmin]
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        qs = AuditLog.objects.all()
        p = self.request.query_params
        if p.get("role") in ROLE_GROUPS:
            qs = qs.filter(actor_role__in=ROLE_GROUPS[p["role"]])
        if p.get("actor"):
            qs = qs.filter(actor_id=p["actor"])
        if p.get("company"):
            qs = qs.filter(company_id=p["company"])
        if p.get("action"):
            qs = qs.filter(action__startswith=p["action"])
        if p.get("from") and (start := _day(p["from"])):
            qs = qs.filter(at__gte=start)
        if p.get("to") and (end := _day(p["to"], end=True)):
            qs = qs.filter(at__lte=end)
        if p.get("q"):
            t = p["q"].strip()
            qs = qs.filter(Q(summary__icontains=t) | Q(target_label__icontains=t) | Q(actor_username__icontains=t))
        return qs

    def list(self, request, *args, **kwargs):
        # exact totals for the whole filtered set (not just this page)
        resp = super().list(request, *args, **kwargs)
        agg = self.filter_queryset(self.get_queryset()).aggregate(
            changes=Count("id", filter=~Q(action__startswith="auth.")),
            signins=Count("id", filter=Q(action="auth.login")),
            failed=Count("id", filter=Q(ok=False)),
        )
        resp.data["stats"] = agg
        return resp
