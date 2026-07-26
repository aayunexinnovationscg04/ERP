"""RBAC / access-resolution tests. Run: .venv/bin/python manage.py test core"""

from django.test import TestCase

from core.access import effective_modules
from core.models import (Company, RolePermission, User, UserModuleOverride)


class AccessTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="C", slug="c")
        # role default: owner may see 'fleet' but not 'billing'
        RolePermission.objects.create(role="owner", module="fleet", allowed=True)
        RolePermission.objects.create(role="owner", module="billing", allowed=False)

    def _owner(self):
        return User.objects.create(username="o", role="owner", company=self.company)

    def test_role_default_applies(self):
        u = self._owner()
        mods = effective_modules(u)
        self.assertIn("fleet", mods)
        self.assertNotIn("billing", mods)

    def test_override_grants(self):
        u = self._owner()
        UserModuleOverride.objects.create(user=u, module="billing", allowed=True)
        self.assertIn("billing", effective_modules(u))

    def test_override_denies(self):
        u = self._owner()
        UserModuleOverride.objects.create(user=u, module="fleet", allowed=False)
        self.assertNotIn("fleet", effective_modules(u))

    def test_superadmin_is_all_access(self):
        sa = User.objects.create(username="sa", role="superadmin")
        from core.modules import MODULE_KEYS
        self.assertEqual(set(effective_modules(sa)), set(MODULE_KEYS))
