"""RBAC / access-resolution tests. Run: .venv/bin/python manage.py test core"""

from django.test import TestCase

from core.access import effective_modules
from core.models import (Company, RolePermission, User, UserModuleOverride)


class AccessTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="C", slug="c")
        # role default: dealer may see 'fleet' but not 'billing'
        RolePermission.objects.create(role="dealer", module="fleet", allowed=True)
        RolePermission.objects.create(role="dealer", module="billing", allowed=False)

    def _dealer(self):
        return User.objects.create(username="o", role="dealer", company=self.company)

    def test_role_default_applies(self):
        u = self._dealer()
        mods = effective_modules(u)
        self.assertIn("fleet", mods)
        self.assertNotIn("billing", mods)

    def test_override_grants(self):
        u = self._dealer()
        UserModuleOverride.objects.create(user=u, module="billing", allowed=True)
        self.assertIn("billing", effective_modules(u))

    def test_override_denies(self):
        u = self._dealer()
        UserModuleOverride.objects.create(user=u, module="fleet", allowed=False)
        self.assertNotIn("fleet", effective_modules(u))

    def test_admin_is_all_access(self):
        sa = User.objects.create(username="sa", role="admin")
        from core.modules import MODULE_KEYS
        self.assertEqual(set(effective_modules(sa)), set(MODULE_KEYS))
