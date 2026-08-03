"""End-to-end API tests: auth, admin RBAC, platform health, company scoping,
driver isolation. Run: .venv/bin/python manage.py test

Throttle rates are raised sky-high here so the login throttle never 429s the
test client (all requests come from 127.0.0.1).
"""

import copy
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from core.models import Company, User
from fleet.models import (Device, Driver, DriverAttendance, Geofence, Vehicle,
                          VehicleDocument)

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


class FleetTableTests(ApiBase):
    """The Fleet page's table + row-expand panel are powered entirely by
    /api/vehicles/ — no client-side sorting or date math. These pin that
    contract: documents/driver ride along in the list payload, and
    ?priority_status= reorders server-side."""

    def setUp(self):
        super().setUp()
        self.v_active = Vehicle.objects.create(
            company=self.c1, registration_number="A-ACTIVE", status=Vehicle.Status.ACTIVE)
        self.v_idle = Vehicle.objects.create(
            company=self.c1, registration_number="B-IDLE", status=Vehicle.Status.IDLE)
        self.v_offline = Vehicle.objects.create(
            company=self.c1, registration_number="C-OFFLINE", status=Vehicle.Status.OFFLINE)
        today = timezone.localdate()
        VehicleDocument.objects.create(
            vehicle=self.v_active, doc_type=VehicleDocument.DocType.INSURANCE,
            number="INS-1", expiry_date=today - timedelta(days=1))  # expired
        VehicleDocument.objects.create(
            vehicle=self.v_active, doc_type=VehicleDocument.DocType.PUC,
            number="PUC-1", expiry_date=today + timedelta(days=10))  # expiring soon
        VehicleDocument.objects.create(
            vehicle=self.v_active, doc_type=VehicleDocument.DocType.RC,
            number="RC-1", expiry_date=today + timedelta(days=365))  # valid

    def _regs(self, data):
        return [v["registration_number"] for v in (data.get("results") if isinstance(data, dict) else data)]

    def test_default_order_is_by_registration_number(self):
        r = self.client_for("owner1", "OwnPass1234").get("/api/vehicles/")
        self.assertEqual(self._regs(r.data), ["A-ACTIVE", "B-IDLE", "C-OFFLINE"])

    def test_priority_status_sorts_that_status_first(self):
        r = self.client_for("owner1", "OwnPass1234").get("/api/vehicles/?priority_status=offline")
        self.assertEqual(self._regs(r.data)[0], "C-OFFLINE")

    def test_invalid_priority_status_falls_back_to_default(self):
        r = self.client_for("owner1", "OwnPass1234").get("/api/vehicles/?priority_status=bogus")
        self.assertEqual(self._regs(r.data), ["A-ACTIVE", "B-IDLE", "C-OFFLINE"])

    def test_documents_carry_computed_expiry_status(self):
        r = self.client_for("owner1", "OwnPass1234").get("/api/vehicles/")
        rows = r.data.get("results") if isinstance(r.data, dict) else r.data
        docs = next(v for v in rows if v["registration_number"] == "A-ACTIVE")["documents"]
        by_number = {d["number"]: d["expiry_status"] for d in docs}
        self.assertEqual(by_number["INS-1"], "expired")
        self.assertEqual(by_number["PUC-1"], "expiring_soon")
        self.assertEqual(by_number["RC-1"], "valid")

    def test_local_name_defaults_sequentially_per_company(self):
        self.assertEqual(self.v_active.local_name, "Vehicle 1")
        self.assertEqual(self.v_idle.local_name, "Vehicle 2")
        self.assertEqual(self.v_offline.local_name, "Vehicle 3")

    def test_granted_owner_can_rename_vehicle(self):
        self.owner1.can_edit = True
        self.owner1.save(update_fields=["can_edit"])
        c = self.client_for("owner1", "OwnPass1234")
        r = c.patch(f"/api/vehicles/{self.v_active.id}/local_name/",
                    {"local_name": "Loader 2"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.v_active.refresh_from_db()
        self.assertEqual(self.v_active.local_name, "Loader 2")

    def test_readonly_owner_cannot_rename_vehicle(self):
        c = self.client_for("owner1", "OwnPass1234")  # can_edit=False by default
        r = c.patch(f"/api/vehicles/{self.v_active.id}/local_name/",
                    {"local_name": "Nope"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_rename_over_10_chars_rejected(self):
        self.owner1.can_edit = True
        self.owner1.save(update_fields=["can_edit"])
        c = self.client_for("owner1", "OwnPass1234")
        r = c.patch(f"/api/vehicles/{self.v_active.id}/local_name/",
                    {"local_name": "WayTooLongName"}, format="json")
        self.assertEqual(r.status_code, 400)


class PilotsTests(ApiBase):
    """The Pilots page (/api/drivers/) — assigned vehicle, attendance, and
    salary. Salary is only in the detail payload, never the list, since the
    list powers a grid other users could be glancing at."""

    def setUp(self):
        super().setUp()
        self.driver_a = Driver.objects.create(
            company=self.c1, name="Ramesh Kumar", phone="9990001111",
            license_no="CG04-2020-001", monthly_salary="18000.00")
        self.veh = Vehicle.objects.create(
            company=self.c1, registration_number="CG04-PILOT-01", active_driver=self.driver_a)
        DriverAttendance.objects.create(
            driver=self.driver_a, date=timezone.localdate(), status=DriverAttendance.Status.PRESENT)
        # a driver in the other company must never show up for owner1
        Driver.objects.create(company=self.c2, name="Other Co Driver")

    def _rows(self, data):
        return data.get("results") if isinstance(data, dict) else data

    def test_owner_sees_only_own_company_drivers(self):
        r = self.client_for("owner1", "OwnPass1234").get("/api/drivers/")
        names = [d["name"] for d in self._rows(r.data)]
        self.assertIn("Ramesh Kumar", names)
        self.assertNotIn("Other Co Driver", names)

    def test_list_carries_assigned_vehicle_but_not_salary(self):
        r = self.client_for("owner1", "OwnPass1234").get("/api/drivers/")
        row = next(d for d in self._rows(r.data) if d["name"] == "Ramesh Kumar")
        self.assertEqual(row["assigned_vehicle"]["registration_number"], "CG04-PILOT-01")
        self.assertNotIn("monthly_salary", row)

    def test_detail_carries_salary_and_attendance(self):
        r = self.client_for("owner1", "OwnPass1234").get(f"/api/drivers/{self.driver_a.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["monthly_salary"], "18000.00")
        self.assertEqual(len(r.data["attendance"]), 1)
        self.assertEqual(r.data["attendance"][0]["status"], "present")

    def test_driver_with_no_vehicle_gets_null_assignment(self):
        lone = Driver.objects.create(company=self.c1, name="Unassigned Driver")
        r = self.client_for("owner1", "OwnPass1234").get(f"/api/drivers/{lone.id}/")
        self.assertIsNone(r.data["assigned_vehicle"])
