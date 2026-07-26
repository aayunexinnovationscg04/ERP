"""Seed the RolePermission matrix from DEFAULT_ACCESS.

Safe to re-run: only creates missing (role, module) rows; never overwrites
values a Super Admin has since changed.

    .venv/bin/python manage.py seed_permissions
"""

from django.core.management.base import BaseCommand

from core.models import RolePermission, User
from core.modules import DEFAULT_ACCESS, MODULE_KEYS


class Command(BaseCommand):
    help = "Populate default role -> module access."

    def handle(self, *args, **options):
        created = 0
        for role, _ in User.Role.choices:
            if role == User.Role.SUPERADMIN:
                continue  # always all-access, not stored
            allowed_set = set(DEFAULT_ACCESS.get(role, []))
            for module in MODULE_KEYS:
                _, was_created = RolePermission.objects.get_or_create(
                    role=role, module=module,
                    defaults={"allowed": module in allowed_set},
                )
                created += int(was_created)
        self.stdout.write(self.style.SUCCESS(f"seeded {created} role-permission row(s)"))
