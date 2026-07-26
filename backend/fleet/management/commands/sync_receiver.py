"""Live bridge: import NEW records from the legacy receiver's events.jsonl into
the ERP Telemetry table, then run the derivation engine on each.

The device posts to the legacy receiver (append-only events.jsonl). This command
runs on a short systemd timer so the ERP reflects new device data within ~1 min.

Identity rule: a device is identified ONLY by its fixed `device_id` (the client IP
is NOT fixed and is never used for identity — it is kept in raw for reference).
Telemetry rows carry raw['_seq'] (the receiver's monotonic seq) so re-runs are
idempotent: a (device, _seq) already present is skipped.

A byte-offset cursor makes each run O(new bytes). If the log is truncated/rotated
(size < cursor) the cursor resets to 0 and the seq-dedup prevents duplicates.

    .venv/bin/python manage.py sync_receiver \
        --path /root/receiver-dashboard/data/events.jsonl [--company <slug>]
"""

import datetime
import json
import os

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Company
from fleet.derivation import process_telemetry
from fleet.models import Device, Telemetry

DEFAULT_PATH = "/root/receiver-dashboard/data/events.jsonl"


def _num(d, *keys):
    for k in keys:
        v = d.get(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return v
    return None


def _flag(d, key):
    v = d.get(key)
    return bool(v) if isinstance(v, bool) else (None if v is None else bool(v))


class Command(BaseCommand):
    help = "Incrementally import new receiver events into Telemetry (live bridge)."

    def add_arguments(self, parser):
        parser.add_argument("--path", default=DEFAULT_PATH)
        parser.add_argument("--company", default=None,
                            help="slug of a company to attach newly-seen devices to")

    def _cursor_path(self, path):
        return path + ".erp_sync_offset"

    def handle(self, *args, **opts):
        path = opts["path"]
        if not os.path.exists(path):
            self.stderr.write(f"receiver log not found: {path}")
            return

        company = None
        if opts["company"]:
            company = Company.objects.filter(slug=opts["company"]).first()

        cursor_file = self._cursor_path(path)
        offset = 0
        try:
            offset = int(open(cursor_file).read().strip())
        except (OSError, ValueError):
            offset = 0
        # log truncated/rotated -> re-scan from start (seq-dedup guards duplicates)
        if offset > os.path.getsize(path):
            offset = 0

        imported = skipped = 0
        with open(path, encoding="utf-8") as fh:
            fh.seek(offset)
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

                # identity: device_id only (never IP)
                device, _ = Device.objects.get_or_create(device_id=did)
                if company and device.company_id is None:
                    device.company = company
                    device.save(update_fields=["company"])

                seq = e.get("seq")
                if seq is not None and Telemetry.objects.filter(
                        device=device, raw___seq=seq).exists():
                    skipped += 1
                    continue

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
                raw["_seq"] = seq
                raw["_client_ip"] = e.get("client_ip", "")  # reference only, not identity

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
                t.save()
                Telemetry.objects.filter(pk=t.pk).update(received_at=received)
                t.refresh_from_db()
                try:
                    process_telemetry(t)
                except Exception as exc:  # never let one bad row stall the bridge
                    self.stderr.write(f"derivation failed for seq={seq}: {exc}")
                imported += 1

            new_offset = fh.tell()

        with open(cursor_file, "w") as cf:
            cf.write(str(new_offset))

        if imported or skipped:
            self.stdout.write(self.style.SUCCESS(
                f"sync: imported {imported}, skipped {skipped}, cursor@{new_offset}"))
