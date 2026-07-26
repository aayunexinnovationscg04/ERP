"""Sweep devices that have gone silent and raise DEVICE_OFFLINE alerts.

Run on an interval (systemd timer or cron), e.g. every 60s:
    .venv/bin/python manage.py mark_offline
"""

from django.core.management.base import BaseCommand

from fleet.derivation import mark_offline


class Command(BaseCommand):
    help = "Flag devices silent past their offline window and raise alerts."

    def handle(self, *args, **options):
        n = mark_offline()
        self.stdout.write(self.style.SUCCESS(f"marked {n} device(s) offline"))
