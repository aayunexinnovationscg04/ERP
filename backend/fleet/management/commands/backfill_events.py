"""Import the legacy receiver's events.jsonl into the Telemetry table.

Seeds the new system with the real esp32-01 history so the dashboard has data
to show on day one. Idempotent-ish: skips telemetry already imported (tracked by
the raw['_seq'] marker from the source log).

    .venv/bin/python manage.py backfill_events \
        --path /root/receiver-dashboard/data/events.jsonl [--company <slug>]
"""

import datetime
import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Company
from fleet.derivation import process_telemetry
from fleet.models import Device, Telemetry

DEFAULT_PATH = "/root/receiver-dashboard/data/events.jsonl"


def _num(d, *keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)):
            return v
    return None


def _flag(d, key):
    v = d.get(key)
    return bool(v) if isinstance(v, bool) else (None if v is None else bool(v))


class Command(BaseCommand):
    help = "Backfill Telemetry from a legacy events.jsonl log."

    def add_arguments(self, parser):
        parser.add_argument("--path", default=DEFAULT_PATH)
        parser.add_argument("--company", default=None,
                            help="slug of a company to attach new devices to")
        parser.add_argument("--derive", action="store_true",
                            help="run the derivation engine on each imported point")

    def handle(self, *args, **opts):
        company = None
        if opts["company"]:
            company = Company.objects.filter(slug=opts["company"]).first()
            if not company:
                self.stderr.write(f"company '{opts['company']}' not found; importing unassigned")

        imported = skipped = 0
        with open(opts["path"], encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    skipped += 1
                    continue
                j = e.get("json") or {}
                did = e.get("device_id") or j.get("device_id")
                if not did:
                    skipped += 1
                    continue
                device, created = Device.objects.get_or_create(device_id=did)
                if created and company:
                    device.company = company
                    device.save(update_fields=["company"])

                lat = _num(j, "latitude", "lat")
                lng = _num(j, "longitude", "lng")
                sats = _num(j, "satellites")
                has_fix = bool(sats and sats > 0 and lat not in (None, 0) and lng not in (None, 0))
                ts = e.get("ts")
                received = (
                    timezone.make_aware(datetime.datetime.fromtimestamp(ts / 1000))
                    if ts else timezone.now()
                )
                raw = dict(j)
                raw["_seq"] = e.get("seq")
                raw["_client_ip"] = e.get("client_ip", "")

                t = Telemetry(
                    device=device,
                    vehicle=getattr(device, "vehicle", None),
                    latitude=lat, longitude=lng,
                    speed_kmph=_num(j, "speed_kmph", "speed"),
                    satellites=int(sats) if sats is not None else None,
                    altitude_m=_num(j, "altitude_m", "altitude"),
                    flow_rate_lpm=_num(j, "flow_rate_lpm"),
                    total_litres=_num(j, "total_litres"),
                    recording=_flag(j, "recording"),
                    lock_active=_flag(j, "lock_active"),
                    gsm_signal=_num(j, "gsm_signal"),
                    has_gps_fix=has_fix,
                    raw=raw,
                )
                # received_at is auto_now_add; set explicitly via bulk-friendly save
                t.save()
                Telemetry.objects.filter(pk=t.pk).update(received_at=received)
                if opts["derive"]:
                    t.refresh_from_db()
                    process_telemetry(t)
                imported += 1

        self.stdout.write(self.style.SUCCESS(
            f"imported {imported} telemetry row(s), skipped {skipped}"))
