"""Admin "Device data": every device that reports in, and the packets it sends.

Devices post to the receiver dashboard, which forwards each packet to the ERP
(ingest/views.py). These read-only endpoints show what arrived, per device.
Admin only.
"""

from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import IsAdmin

from .models import Device, Telemetry


def _packet(t):
    return {
        "id": t.id,
        "received_at": t.received_at,
        "latitude": t.latitude, "longitude": t.longitude,
        "speed_kmph": t.speed_kmph, "satellites": t.satellites, "has_gps_fix": t.has_gps_fix,
        "total_litres": t.total_litres, "flow_rate_lpm": t.flow_rate_lpm,
        "lock_active": t.lock_active, "recording": t.recording, "gsm_signal": t.gsm_signal,
        "seq": t.raw.get("_seq"), "client_ip": t.raw.get("_client_ip"),
        "raw": {k: v for k, v in t.raw.items() if not k.startswith("_")},
    }


class IngestDevicesView(APIView):
    """GET /api/admin/ingest/devices — every device with its reporting summary."""

    permission_classes = [IsAdmin]

    def get(self, request):
        since = timezone.now() - timedelta(hours=24)
        devices = (Device.objects.select_related("company", "vehicle")
                   .annotate(total=Count("telemetry"),
                             last_24h=Count("telemetry", filter=Q(telemetry__received_at__gte=since)))
                   .order_by("-last_seen", "device_id"))
        devices = list(devices)
        latest = {}
        for t in (Telemetry.objects.filter(device_id__in=[d.id for d in devices])
                  .order_by("device_id", "-received_at").distinct("device_id")):
            latest[t.device_id] = _packet(t)
        out = []
        for d in devices:
            vehicle = getattr(d, "vehicle", None)
            out.append({
                "id": d.id, "device_id": d.device_id, "label": d.label,
                "company": d.company.name if d.company else None,
                "vehicle": vehicle.registration_number if vehicle else None,
                "online": d.online, "last_seen": d.last_seen, "last_ip": d.last_ip,
                "firmware": d.firmware_version, "sim": d.sim_number,
                "packets_total": d.total, "packets_24h": d.last_24h,
                "latest": latest.get(d.id),
            })
        return Response(out)


class IngestPacketsView(APIView):
    """GET /api/admin/ingest/devices/<pk>/packets?limit=50 — newest packets first."""

    permission_classes = [IsAdmin]

    def get(self, request, pk):
        try:
            limit = max(1, min(200, int(request.query_params.get("limit", 50))))
        except ValueError:
            limit = 50
        rows = Telemetry.objects.filter(device_id=pk).order_by("-received_at")[:limit]
        return Response([_packet(t) for t in rows])
