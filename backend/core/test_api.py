"""End-to-end API tests: auth, admin RBAC, platform health, company scoping,
driver isolation. Run: .venv/bin/python manage.py test

Throttle rates are raised sky-high here so the login throttle never 429s the
test client (all requests come from 127.0.0.1).
"""

import copy

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from core.models import Company, User
from fleet.models import Device, Driver, Geofence, Vehicle

_DRF = copy.deepcopy(settings.REST_FRAMEWORK)
_DRF["DEFAULT_THROTTLE_RATES"] = {
    "anon": "100000/min", "user": "100000/min", "login": "100000/min",
}


@override_settings(REST_FRAMEWORK=_DRF)
class ApiBase(TestCase):
    def setUp(self):
        cache.clear()
        self.c1 = Company.objects.create(name="Acme", slug="acme")
        self.c2 = Company.objects.create(name="Beta", slug="beta")
        self.sa = self._user("sa", "superadmin", None, "SaPass1234")
        self.owner1 = self._user("owner1", "owner", self.c1, "OwnPass1234")
        self.owner2 = self._user("owner2", "owner", self.c2, "OwnPass5678")
        self.driver1 = self._user("driver1", "driver", self.c1, "DrvPass1234")

    def _user(self, uname, role, company, pw):
        u = User.objects.create(username=uname, role=role, company=company)
        u.set_password(pw)
        u.save()
        return u

    def client_for(self, username, password):
        c = APIClient()
        r = c.post("/api/auth/login",
                   {"username": username, "password": password}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        c.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])
        return c


class AuthTests(ApiBase):
    def test_login_returns_tokens_and_user(self):
        r = APIClient().post("/api/auth/login",
                             {"username": "owner1", "password": "OwnPass1234"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertIn("refresh", r.data)
        self.assertEqual(r.data["user"]["role"], "owner")

    def test_bad_password_401(self):
        r = APIClient().post("/api/auth/login",
                             {"username": "owner1", "password": "wrong"}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_me_requires_auth(self):
        self.assertEqual(APIClient().get("/api/auth/me").status_code, 401)

    def test_me_returns_effective_modules(self):
        r = self.client_for("owner1", "OwnPass1234").get("/api/auth/me")
        self.assertEqual(r.status_code, 200)
        self.assertIn("modules", r.data)


class AdminRbacTests(ApiBase):
    def test_superadmin_lists_users(self):
        self.assertEqual(self.client_for("sa", "SaPass1234").get("/api/admin/users/").status_code, 200)

    def test_owner_blocked_from_admin_users(self):
        self.assertEqual(self.client_for("owner1", "OwnPass1234").get("/api/admin/users/").status_code, 403)

    def test_owner_blocked_from_health(self):
        self.assertEqual(self.client_for("owner1", "OwnPass1234").get("/api/admin/health").status_code, 403)

    def test_health_ok_for_superadmin(self):
        r = self.client_for("sa", "SaPass1234").get("/api/admin/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "ok")
        self.assertTrue(r.data["database"]["ok"])
        self.assertEqual(r.data["counts"]["companies"], 2)
        self.assertIn("ingest", r.data)

    def test_admin_creates_user(self):
        c = self.client_for("sa", "SaPass1234")
        r = c.post("/api/admin/users/",
                   {"username": "newdrv", "password": "NewDrvPass99",
                    "role": "driver", "company": self.c1.id}, format="json")
        self.assertIn(r.status_code, (200, 201), r.content)
        self.assertTrue(User.objects.filter(username="newdrv").exists())


class CompanyScopingTests(ApiBase):
    def setUp(self):
        super().setUp()
        self.g1 = Geofence.objects.create(company=self.c1, name="Depot", kind="circle",
                                          center_lat=21.1, center_lng=81.6, radius_m=200)
        self.g2 = Geofence.objects.create(company=self.c2, name="Yard", kind="circle",
                                          center_lat=20.0, center_lng=80.0, radius_m=200)

    def _names(self, data):
        return [g["name"] for g in (data.get("results") if isinstance(data, dict) else data)]

    def _grant_edit(self, user):
        user.can_edit = True
        user.save(update_fields=["can_edit"])

    def test_owner_sees_only_own_geofences(self):
        # read is allowed even without edit rights
        r = self.client_for("owner1", "OwnPass1234").get("/api/geofences/")
        names = self._names(r.data)
        self.assertIn("Depot", names)
        self.assertNotIn("Yard", names)

    def test_readonly_owner_cannot_write(self):
        # owner1 has can_edit=False by default -> read OK, write 403
        c = self.client_for("owner1", "OwnPass1234")
        self.assertEqual(c.get("/api/geofences/").status_code, 200)
        r = c.post("/api/geofences/",
                   {"name": "Nope", "kind": "circle", "center_lat": 21.2,
                    "center_lng": 81.7, "radius_m": 150, "purpose": "allowed", "active": True},
                   format="json")
        self.assertEqual(r.status_code, 403)
        self.assertFalse(Geofence.objects.filter(name="Nope").exists())

    def test_granted_owner_creates_geofence_scoped_to_company(self):
        self._grant_edit(self.owner1)
        c = self.client_for("owner1", "OwnPass1234")
        r = c.post("/api/geofences/",
                   {"name": "NewZone", "kind": "circle", "center_lat": 21.2,
                    "center_lng": 81.7, "radius_m": 150, "purpose": "allowed", "active": True},
                   format="json")
        self.assertIn(r.status_code, (200, 201), r.content)
        self.assertEqual(Geofence.objects.get(name="NewZone").company_id, self.c1.id)

    def test_granted_owner_cannot_touch_other_company_geofence(self):
        self._grant_edit(self.owner1)
        c = self.client_for("owner1", "OwnPass1234")
        self.assertEqual(c.delete(f"/api/geofences/{self.g2.id}/").status_code, 404)


class DriverApiTests(ApiBase):
    def setUp(self):
        super().setUp()
        self.dev = Device.objects.create(device_id="dev-1", company=self.c1)
        self.veh = Vehicle.objects.create(company=self.c1, registration_number="RJ-01", device=self.dev)
        self.prof = Driver.objects.create(company=self.c1, user=self.driver1, name="D One")
        self.veh.active_driver = self.prof
        self.veh.save()

    def test_driver_blocked_from_owner_vehicles(self):
        self.assertEqual(self.client_for("driver1", "DrvPass1234").get("/api/vehicles/").status_code, 403)

    def test_driver_summary_shows_assigned_vehicle(self):
        r = self.client_for("driver1", "DrvPass1234").get("/api/driver/summary")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["assigned"])
        self.assertEqual(r.data["vehicle"]["registration_number"], "RJ-01")

    def test_unassigned_driver_gets_assigned_false(self):
        self._user("drv2", "driver", self.c1, "Drv2Pass1234")
        r = self.client_for("drv2", "Drv2Pass1234").get("/api/driver/summary")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.data["assigned"])

    def test_owner_blocked_from_driver_endpoints(self):
        self.assertEqual(self.client_for("owner1", "OwnPass1234").get("/api/driver/summary").status_code, 403)
