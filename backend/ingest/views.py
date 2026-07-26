"""Device telemetry ingest — firmware-compatible with the existing esp32-01.

Contract preserved from the old receiver so no re-flashing is needed:
  POST /api/telemetry   header  X-Auth: <ingest token>   body: JSON telemetry
Permissive: any content type is accepted and stored; nothing is rejected on shape.
Commands queued for the device ride back in the reply, exactly-once.
"""

import hmac
import json

from django.conf import settings
from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from fleet.derivation import process_telemetry
from fleet.models import Device, Telemetry
from ingest.models import Command

ID_KEYS = ("device_id", "deviceId", "device", "id", "mac", "chip_id", "chipId", "serial", "uuid", "name")


def _token_ok(request):
    token = settings.INGEST_TOKEN
    for h in ("HTTP_X_AUTH", "HTTP_X_AUTH_TOKEN", "HTTP_X_TOKEN"):
        v = request.META.get(h)
        if v and hmac.compare_digest(v.strip(), token):
            return True
    for k in ("auth", "token", "key"):
        v = request.GET.get(k)
        if v and hmac.compare_digest(v.strip(), token):
            return True
    return False


def _client_ip(request):
    fwd = request.META.get("HTTP_X_FORWARDED_FOR")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _identify(request, parsed):
    for h in ("HTTP_X_DEVICE_ID", "HTTP_X_DEVICE", "HTTP_X_CLIENT_ID", "HTTP_DEVICE_ID"):
        v = request.META.get(h)
        if v:
            return v.strip(), "header"
    if isinstance(parsed, dict):
        for k in ID_KEYS:
            v = parsed.get(k)
            if isinstance(v, (str, int)) and str(v).strip():
                return str(v).strip(), "body"
    for k in ID_KEYS:
        v = request.GET.get(k)
        if v and str(v).strip():
            return str(v).strip(), "query"
    return _client_ip(request), "ip"


def _num(parsed, *keys):
    for k in keys:
        v = parsed.get(k)
        if isinstance(v, (int, float)):
            return v
    return None


def _flag(parsed, key):
    v = parsed.get(key)
    return bool(v) if isinstance(v, bool) else (None if v is None else bool(v))


class TelemetryIngestView(APIView):
    authentication_classes = []          # device is not a JWT user
    permission_classes = [AllowAny]      # auth is the shared ingest token, checked below

    def post(self, request):
        if not _token_ok(request):
            return Response({"error": "unauthorised"}, status=401)

        raw = request.body or b""
        text = raw.decode("utf-8", "replace")
        parsed = {}
        stripped = text.strip()
        if stripped[:1] in ("{", "["):
            try:
                parsed = json.loads(stripped)
            except ValueError:
                parsed = {}
        if not isinstance(parsed, dict):
            parsed = {}

        device_id, id_source = _identify(request, parsed)
        client_ip = _client_ip(request)
        device, _ = Device.objects.get_or_create(device_id=device_id)

        lat = _num(parsed, "latitude", "lat")
        lng = _num(parsed, "longitude", "lng", "lon")
        sats = _num(parsed, "satellites", "sats")
        has_fix = bool(sats and sats > 0 and lat not in (None, 0) and lng not in (None, 0))

        raw_store = dict(parsed) if parsed else {"_text": text[:2000]}
        raw_store["_client_ip"] = client_ip
        raw_store["_id_source"] = id_source

        t = Telemetry.objects.create(
            device=device,
            vehicle=getattr(device, "vehicle", None),
            latitude=lat,
            longitude=lng,
            speed_kmph=_num(parsed, "speed_kmph", "speed"),
            satellites=int(sats) if sats is not None else None,
            altitude_m=_num(parsed, "altitude_m", "altitude", "alt"),
            flow_rate_lpm=_num(parsed, "flow_rate_lpm", "flow_rate"),
            total_litres=_num(parsed, "total_litres", "total_liters", "litres"),
            recording=_flag(parsed, "recording"),
            lock_active=_flag(parsed, "lock_active"),
            gsm_signal=_num(parsed, "gsm_signal", "signal"),
            has_gps_fix=has_fix,
            raw=raw_store,
        )

        try:
            process_telemetry(t)
        except Exception:  # derivation must never break ingest / lose a record
            import logging
            logging.getLogger("ingest").exception("derivation failed for telemetry %s", t.pk)

        # Drain queued commands for this device (exactly-once).
        pending = list(Command.objects.filter(device=device, status=Command.Status.QUEUED).order_by("created_at"))
        commands = []
        if pending:
            now = timezone.now()
            for c in pending:
                commands.append({
                    "id": c.id, "payload": c.payload,
                    "content_type": c.content_type, "ts": int(c.created_at.timestamp() * 1000),
                })
            Command.objects.filter(pk__in=[c.id for c in pending]).update(
                status=Command.Status.DELIVERED, delivered_at=now
            )

        return Response({
            "ok": True,
            "device_id": device_id,
            "received": len(raw),
            "commands": commands,
        })
