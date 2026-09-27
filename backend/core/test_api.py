"""End-to-end API tests: auth, admin RBAC, platform health, company scoping,
pilot isolation. Run: .venv/bin/python manage.py test

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
from fleet.models import (Device, Pilot, PilotAttendance, Geofence, Vehicle,
                          VehicleDocument)

_DRF = copy.deepcopy(settings.REST_FRAMEWORK)
_DRF["DEFAULT_THROTTLE_RATES"] = {
    "anon": "100000/min", "user": "100000/min", "login": "100000/min",
    "refresh": "100000/min",
}


@override_settings(REST_FRAMEWORK=_DRF)
class ApiBase(TestCase):
    def setUp(self):
        cache.clear()
        self.c1 = Company.objects.create(name="Acme", slug="acme")
        self.c2 = Company.objects.create(name="Beta", slug="beta")
        self.sa = self._user("sa", "admin", None, "SaPass1234")
        self.dealer1 = self._user("dealer1", "dealer", self.c1, "OwnPass1234")
        self.dealer2 = self._user("dealer2", "dealer", self.c2, "OwnPass5678")
        self.pilot1 = self._user("pilot1", "pilot", self.c1, "DrvPass1234")

    def _user(self, uname, role, company, pw):
        u = User.objects.create(username=uname, role=role, company=company)
        u.set_password(pw)
        u.save()
        return u

    PORTAL_FOR_ROLE = {"admin": "admin", "dealer": "dealer", "manager": "dealer", "pilot": "pilot"}

    def login(self, username, password, portal=None, client=None):
        c = client or APIClient()
        portal = portal or self.PORTAL_FOR_ROLE[User.objects.get(username=username).role]
        return c, c.post("/api/auth/login", {"username": username, "password": password},
                         format="json", HTTP_X_FGX_PORTAL=portal)

    def client_for(self, username, password):
        c, r = self.login(username, password)
        self.assertEqual(r.status_code, 200, r.content)
        c.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])
        return c


class AuthTests(ApiBase):
    def test_login_returns_access_and_sets_httponly_refresh_cookie(self):
        _, r = self.login("dealer1", "OwnPass1234")
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertNotIn("refresh", r.data)          # never exposed to JS
        self.assertEqual(r.data["user"]["role"], "dealer")
        ck = r.cookies["fgx_rt_dealer"]
        self.assertTrue(ck["httponly"])
        self.assertTrue(ck["secure"])
        self.assertEqual(ck["samesite"], "Strict")
        self.assertEqual(ck["path"], "/api/auth/")

    def test_bad_password_401(self):
        _, r = self.login("dealer1", "wrong", portal="dealer")
        self.assertEqual(r.status_code, 401)

    def test_me_requires_auth(self):
        self.assertEqual(APIClient().get("/api/auth/me").status_code, 401)

    def test_me_returns_effective_modules(self):
        r = self.client_for("dealer1", "OwnPass1234").get("/api/auth/me")
        self.assertEqual(r.status_code, 200)
        self.assertIn("modules", r.data)


class AdminRbacTests(ApiBase):
    def test_admin_lists_users(self):
        self.assertEqual(self.client_for("sa", "SaPass1234").get("/api/admin/users/").status_code, 200)

    def test_dealer_blocked_from_admin_users(self):
        self.assertEqual(self.client_for("dealer1", "OwnPass1234").get("/api/admin/users/").status_code, 403)

    def test_dealer_blocked_from_health(self):
        self.assertEqual(self.client_for("dealer1", "OwnPass1234").get("/api/admin/health").status_code, 403)

    def test_health_ok_for_admin(self):
        r = self.client_for("sa", "SaPass1234").get("/api/admin/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["status"], "ok")
        self.assertTrue(r.data["database"]["ok"])
        self.assertEqual(r.data["counts"]["companies"], 2)
        self.assertIn("ingest", r.data)

    def test_admin_creates_user(self):
        c = self.client_for("sa", "SaPass1234")
        r = c.post("/api/admin/users/",
                   {"username": "newplt", "password": "NewDrvPass99", "phone": "+91 98765 43210",
                    "role": "pilot", "company": self.c1.id}, format="json")
        self.assertIn(r.status_code, (200, 201), r.content)
        self.assertTrue(User.objects.filter(username="newplt").exists())


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

    def test_dealer_sees_only_own_geofences(self):
        # read is allowed even without edit rights
        r = self.client_for("dealer1", "OwnPass1234").get("/api/geofences/")
        names = self._names(r.data)
        self.assertIn("Depot", names)
        self.assertNotIn("Yard", names)

    def test_readonly_dealer_cannot_write(self):
        # dealer1 has can_edit=False by default -> read OK, write 403
        c = self.client_for("dealer1", "OwnPass1234")
        self.assertEqual(c.get("/api/geofences/").status_code, 200)
        r = c.post("/api/geofences/",
                   {"name": "Nope", "kind": "circle", "center_lat": 21.2,
                    "center_lng": 81.7, "radius_m": 150, "purpose": "allowed", "active": True},
                   format="json")
        self.assertEqual(r.status_code, 403)
        self.assertFalse(Geofence.objects.filter(name="Nope").exists())

    def test_granted_dealer_creates_geofence_scoped_to_company(self):
        self._grant_edit(self.dealer1)
        c = self.client_for("dealer1", "OwnPass1234")
        r = c.post("/api/geofences/",
                   {"name": "NewZone", "kind": "circle", "center_lat": 21.2,
                    "center_lng": 81.7, "radius_m": 150, "purpose": "allowed", "active": True},
                   format="json")
        self.assertIn(r.status_code, (200, 201), r.content)
        self.assertEqual(Geofence.objects.get(name="NewZone").company_id, self.c1.id)

    def test_granted_dealer_cannot_touch_other_company_geofence(self):
        self._grant_edit(self.dealer1)
        c = self.client_for("dealer1", "OwnPass1234")
        self.assertEqual(c.delete(f"/api/geofences/{self.g2.id}/").status_code, 404)


class PilotApiTests(ApiBase):
    def setUp(self):
        super().setUp()
        self.dev = Device.objects.create(device_id="dev-1", company=self.c1)
        self.veh = Vehicle.objects.create(company=self.c1, registration_number="RJ-01", device=self.dev)
        self.prof = Pilot.objects.create(company=self.c1, user=self.pilot1, name="D One")
        self.veh.active_pilot = self.prof
        self.veh.save()

    def test_pilot_blocked_from_dealer_vehicles(self):
        self.assertEqual(self.client_for("pilot1", "DrvPass1234").get("/api/vehicles/").status_code, 403)

    def test_pilot_summary_shows_assigned_vehicle(self):
        r = self.client_for("pilot1", "DrvPass1234").get("/api/pilot/summary")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.data["assigned"])
        self.assertEqual(r.data["vehicle"]["registration_number"], "RJ-01")

    def test_unassigned_pilot_gets_assigned_false(self):
        self._user("plt2", "pilot", self.c1, "Drv2Pass1234")
        r = self.client_for("plt2", "Drv2Pass1234").get("/api/pilot/summary")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.data["assigned"])

    def test_dealer_blocked_from_pilot_endpoints(self):
        self.assertEqual(self.client_for("dealer1", "OwnPass1234").get("/api/pilot/summary").status_code, 403)


class FleetTableTests(ApiBase):
    """The Fleet page's table + row-expand panel are powered entirely by
    /api/vehicles/ — no client-side sorting or date math. These pin that
    contract: documents/pilot ride along in the list payload, and
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
        r = self.client_for("dealer1", "OwnPass1234").get("/api/vehicles/")
        self.assertEqual(self._regs(r.data), ["A-ACTIVE", "B-IDLE", "C-OFFLINE"])

    def test_priority_status_sorts_that_status_first(self):
        r = self.client_for("dealer1", "OwnPass1234").get("/api/vehicles/?priority_status=offline")
        self.assertEqual(self._regs(r.data)[0], "C-OFFLINE")

    def test_invalid_priority_status_falls_back_to_default(self):
        r = self.client_for("dealer1", "OwnPass1234").get("/api/vehicles/?priority_status=bogus")
        self.assertEqual(self._regs(r.data), ["A-ACTIVE", "B-IDLE", "C-OFFLINE"])

    def test_documents_carry_computed_expiry_status(self):
        r = self.client_for("dealer1", "OwnPass1234").get("/api/vehicles/")
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

    def test_granted_dealer_can_rename_vehicle(self):
        self.dealer1.can_edit = True
        self.dealer1.save(update_fields=["can_edit"])
        c = self.client_for("dealer1", "OwnPass1234")
        r = c.patch(f"/api/vehicles/{self.v_active.id}/local_name/",
                    {"local_name": "Loader 2"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.v_active.refresh_from_db()
        self.assertEqual(self.v_active.local_name, "Loader 2")

    def test_readonly_dealer_cannot_rename_vehicle(self):
        c = self.client_for("dealer1", "OwnPass1234")  # can_edit=False by default
        r = c.patch(f"/api/vehicles/{self.v_active.id}/local_name/",
                    {"local_name": "Nope"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_rename_over_10_chars_rejected(self):
        self.dealer1.can_edit = True
        self.dealer1.save(update_fields=["can_edit"])
        c = self.client_for("dealer1", "OwnPass1234")
        r = c.patch(f"/api/vehicles/{self.v_active.id}/local_name/",
                    {"local_name": "WayTooLongName"}, format="json")
        self.assertEqual(r.status_code, 400)


class PilotsTests(ApiBase):
    """The Pilots page (/api/pilots/) — assigned vehicle, attendance, and
    salary. Salary is only in the detail payload, never the list, since the
    list powers a grid other users could be glancing at."""

    def setUp(self):
        super().setUp()
        self.pilot_a = Pilot.objects.create(
            company=self.c1, name="Ramesh Kumar", phone="9990001111",
            license_no="CG04-2020-001", monthly_salary="18000.00")
        self.veh = Vehicle.objects.create(
            company=self.c1, registration_number="CG04-PILOT-01", active_pilot=self.pilot_a)
        PilotAttendance.objects.create(
            pilot=self.pilot_a, date=timezone.localdate(), status=PilotAttendance.Status.PRESENT)
        # a pilot in the other company must never show up for dealer1
        Pilot.objects.create(company=self.c2, name="Other Co Pilot")

    def _rows(self, data):
        return data.get("results") if isinstance(data, dict) else data

    def test_dealer_sees_only_own_company_pilots(self):
        r = self.client_for("dealer1", "OwnPass1234").get("/api/pilots/")
        names = [d["name"] for d in self._rows(r.data)]
        self.assertIn("Ramesh Kumar", names)
        self.assertNotIn("Other Co Pilot", names)

    def test_list_carries_assigned_vehicle_but_not_salary(self):
        r = self.client_for("dealer1", "OwnPass1234").get("/api/pilots/")
        row = next(d for d in self._rows(r.data) if d["name"] == "Ramesh Kumar")
        self.assertEqual(row["assigned_vehicle"]["registration_number"], "CG04-PILOT-01")
        self.assertNotIn("monthly_salary", row)

    def test_detail_carries_salary_and_attendance(self):
        r = self.client_for("dealer1", "OwnPass1234").get(f"/api/pilots/{self.pilot_a.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["monthly_salary"], "18000.00")
        self.assertEqual(len(r.data["attendance"]), 1)
        self.assertEqual(r.data["attendance"][0]["status"], "present")

    def test_pilot_with_no_vehicle_gets_null_assignment(self):
        lone = Pilot.objects.create(company=self.c1, name="Unassigned Pilot")
        r = self.client_for("dealer1", "OwnPass1234").get(f"/api/pilots/{lone.id}/")
        self.assertIsNone(r.data["assigned_vehicle"])


class TokenSessionTests(ApiBase):
    """Access/refresh lifecycle: portal lock, rotation, replay, logout, revocation."""

    def refresh(self, c, portal):
        return c.post("/api/auth/refresh", HTTP_X_FGX_PORTAL=portal)

    def test_login_requires_portal_header(self):
        r = APIClient().post("/api/auth/login",
                             {"username": "dealer1", "password": "OwnPass1234"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_role_locked_to_its_portal(self):
        for user, pw, portal in [("dealer1", "OwnPass1234", "admin"),
                                 ("pilot1", "DrvPass1234", "dealer"),
                                 ("sa", "SaPass1234", "pilot"),
                                 ("dealer1", "OwnPass1234", "pilot")]:
            c, r = self.login(user, pw, portal=portal)
            self.assertEqual(r.status_code, 403, (user, portal))
            self.assertNotIn(f"fgx_rt_{portal}", r.cookies)

    def test_all_three_portals_login_and_refresh(self):
        for user, pw, portal in [("sa", "SaPass1234", "admin"),
                                 ("dealer1", "OwnPass1234", "dealer"),
                                 ("pilot1", "DrvPass1234", "pilot")]:
            c, r = self.login(user, pw)
            self.assertEqual(r.status_code, 200, portal)
            r2 = self.refresh(c, portal)
            self.assertEqual(r2.status_code, 200, portal)
            self.assertIn("access", r2.data)
            self.assertEqual(r2.data["user"]["username"], user)
            c.credentials(HTTP_AUTHORIZATION="Bearer " + r2.data["access"])
            self.assertEqual(c.get("/api/auth/me").status_code, 200)

    def test_refresh_rotates_and_old_token_is_rejected(self):
        c, _ = self.login("dealer1", "OwnPass1234")
        old = c.cookies["fgx_rt_dealer"].value
        r = self.refresh(c, "dealer")
        self.assertEqual(r.status_code, 200)
        self.assertNotEqual(c.cookies["fgx_rt_dealer"].value, old)
        replay = APIClient()
        replay.cookies["fgx_rt_dealer"] = old
        self.assertEqual(self.refresh(replay, "dealer").status_code, 401)

    def test_refresh_needs_cookie_and_matching_portal(self):
        self.assertEqual(self.refresh(APIClient(), "dealer").status_code, 401)
        c, _ = self.login("dealer1", "OwnPass1234")
        other = APIClient()
        other.cookies["fgx_rt_admin"] = c.cookies["fgx_rt_dealer"].value
        self.assertEqual(self.refresh(other, "admin").status_code, 401)
        self.assertEqual(c.post("/api/auth/refresh").status_code, 403)  # no header

    def test_logout_revokes_refresh(self):
        c, _ = self.login("pilot1", "DrvPass1234")
        rt = c.cookies["fgx_rt_pilot"].value
        self.assertEqual(c.post("/api/auth/logout", HTTP_X_FGX_PORTAL="pilot").status_code, 204)
        again = APIClient()
        again.cookies["fgx_rt_pilot"] = rt
        self.assertEqual(self.refresh(again, "pilot").status_code, 401)

    def test_password_change_kills_access_and_refresh(self):
        c, r = self.login("dealer1", "OwnPass1234")
        c.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])
        self.dealer1.set_password("NewPass9999")
        self.dealer1.save()
        self.assertEqual(c.get("/api/auth/me").status_code, 401)
        self.assertEqual(self.refresh(c, "dealer").status_code, 401)

    def test_company_change_by_admin_kills_sessions(self):
        c, r = self.login("dealer1", "OwnPass1234")
        admin = self.client_for("sa", "SaPass1234")
        admin.patch(f"/api/admin/users/{self.dealer1.pk}/", {"company": self.c2.id}, format="json")
        c.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])
        self.assertEqual(c.get("/api/auth/me").status_code, 401)

    def test_deactivated_user_cannot_refresh(self):
        c, _ = self.login("dealer1", "OwnPass1234")
        User.objects.filter(pk=self.dealer1.pk).update(is_active=False)
        self.assertEqual(self.refresh(c, "dealer").status_code, 401)

    def test_logout_all_revokes_every_session(self):
        c1, r1 = self.login("dealer1", "OwnPass1234")
        c2, _ = self.login("dealer1", "OwnPass1234")
        c1.credentials(HTTP_AUTHORIZATION="Bearer " + r1.data["access"])
        self.assertEqual(c1.post("/api/auth/logout-all", HTTP_X_FGX_PORTAL="dealer").status_code, 204)
        self.assertEqual(c1.get("/api/auth/me").status_code, 401)
        self.assertEqual(self.refresh(c2, "dealer").status_code, 401)

    def test_absolute_session_cap(self):
        c, _ = self.login("sa", "SaPass1234")
        from unittest import mock
        import time as _t
        later = _t.time() + 13 * 3600
        with mock.patch("core.tokens.time.time", return_value=later), \
                mock.patch("rest_framework_simplejwt.tokens.aware_utcnow",
                           return_value=timezone.now() + timedelta(hours=11)):
            self.assertEqual(self.refresh(c, "admin").status_code, 401)


class ModuleAccessTests(ApiBase):
    """Role Management / per-user module switches are enforced by the API."""

    def setUp(self):
        super().setUp()
        from core.models import RolePermission, UserModuleOverride
        self.RolePermission, self.Override = RolePermission, UserModuleOverride

    def test_defaults_allow_normal_use(self):
        c = self.client_for("dealer1", "OwnPass1234")
        for url in ["/api/vehicles/", "/api/alerts/", "/api/geofences/", "/api/pilots/"]:
            self.assertEqual(c.get(url).status_code, 200, url)

    def test_role_switch_blocks_endpoint(self):
        self.RolePermission.objects.update_or_create(role="dealer", module="drivers", defaults={"allowed": False})
        c = self.client_for("dealer1", "OwnPass1234")
        self.assertEqual(c.get("/api/pilots/").status_code, 403)
        self.assertEqual(c.get("/api/vehicles/").status_code, 200)   # other modules unaffected

    def test_user_override_beats_role_default(self):
        self.Override.objects.create(user=self.dealer1, module="geofences", allowed=False)
        self.Override.objects.create(user=self.dealer1, module="live_map", allowed=False)
        c = self.client_for("dealer1", "OwnPass1234")
        self.assertEqual(c.get("/api/geofences/").status_code, 403)
        other = self.client_for("dealer2", "OwnPass5678")
        self.assertEqual(other.get("/api/geofences/").status_code, 200)

    def test_endpoint_needs_any_one_of_its_modules(self):
        for m in ["alerts", "dashboard", "fuel", "drivers"]:
            self.Override.objects.create(user=self.dealer1, module=m, allowed=False)
        c = self.client_for("dealer1", "OwnPass1234")
        self.assertEqual(c.get("/api/alerts/").status_code, 403)
        self.Override.objects.filter(user=self.dealer1, module="fuel").update(allowed=True)
        self.assertEqual(c.get("/api/alerts/").status_code, 200)

    def test_pilot_modules(self):
        self.Override.objects.create(user=self.pilot1, module="driver_trips", allowed=False)
        c = self.client_for("pilot1", "DrvPass1234")
        self.assertEqual(c.get("/api/pilot/trips").status_code, 403)
        self.assertEqual(c.get("/api/pilot/summary").status_code, 200)

    def test_admin_never_blocked(self):
        c = self.client_for("sa", "SaPass1234")
        self.assertEqual(c.get("/api/pilots/").status_code, 200)


class SuspendedCompanyTests(ApiBase):
    def test_suspended_company_is_read_only(self):
        self.dealer1.can_edit = True
        self.dealer1.save()
        self.c1.status = Company.Status.SUSPENDED
        self.c1.save()
        c = self.client_for("dealer1", "OwnPass1234")
        self.assertFalse(c.get("/api/auth/me").data["may_write"])
        self.assertEqual(c.get("/api/geofences/").status_code, 200)
        r = c.post("/api/geofences/", {"name": "X", "kind": "restricted", "center_lat": 1,
                                       "center_lng": 1, "radius_m": 100}, format="json")
        self.assertEqual(r.status_code, 403)


class ViewAsTests(ApiBase):
    """Admin 'view as': one-time ticket -> read-only session on the user's portal."""

    def ticket_for(self, user):
        admin = self.client_for("sa", "SaPass1234")
        return admin.post(f"/api/admin/users/{user.pk}/view-as/")

    def redeem(self, ticket, portal):
        return APIClient().post("/api/auth/view-as", {"ticket": ticket}, format="json",
                                HTTP_X_FGX_PORTAL=portal)

    def test_dealer_view_is_read_only(self):
        r = self.ticket_for(self.dealer1)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["portal"], "dealer")
        v = self.redeem(r.data["ticket"], "dealer")
        self.assertEqual(v.status_code, 200)
        self.assertNotIn("fgx_rt_dealer", v.cookies)            # never a refresh cookie
        self.assertTrue(v.data["user"]["view_only"])
        self.assertFalse(v.data["user"]["may_write"])
        c = APIClient(); c.credentials(HTTP_AUTHORIZATION="Bearer " + v.data["access"])
        self.assertEqual(c.get("/api/vehicles/").status_code, 200)
        self.assertEqual(c.get("/api/auth/me").data["username"], "dealer1")
        r = c.post("/api/geofences/", {"name": "x"}, format="json")
        self.assertEqual(r.status_code, 403)

    def test_ticket_is_single_use_and_portal_bound(self):
        t = self.ticket_for(self.pilot1).data["ticket"]
        self.assertEqual(self.redeem(t, "dealer").status_code, 401)   # wrong portal
        self.assertEqual(self.redeem(t, "pilot").status_code, 200)
        self.assertEqual(self.redeem(t, "pilot").status_code, 401)    # already used

    def test_ticket_expires(self):
        from core.models import ViewAsTicket
        t = self.ticket_for(self.dealer1).data["ticket"]
        ViewAsTicket.objects.filter(jti=t).update(expires_at=timezone.now() - timedelta(seconds=1))
        self.assertEqual(self.redeem(t, "dealer").status_code, 401)

    def test_only_admins_can_issue_and_admins_cannot_be_viewed(self):
        dealer = self.client_for("dealer1", "OwnPass1234")
        self.assertEqual(dealer.post(f"/api/admin/users/{self.dealer2.pk}/view-as/").status_code, 403)
        self.assertEqual(self.ticket_for(self.sa).status_code, 403)

    def test_view_ends_when_admin_loses_rights(self):
        v = self.redeem(self.ticket_for(self.dealer1).data["ticket"], "dealer")
        c = APIClient(); c.credentials(HTTP_AUTHORIZATION="Bearer " + v.data["access"])
        User.objects.filter(pk=self.sa.pk).update(is_active=False)
        self.assertEqual(c.get("/api/vehicles/").status_code, 401)


class AdminUserRulesTests(ApiBase):
    """Admin console user rules: dealer/pilot only, phone required, role fixed, password reset."""

    def admin(self):
        return self.client_for("sa", "SaPass1234")

    def test_phone_required_and_only_dealer_or_pilot(self):
        c = self.admin()
        base = {"username": "nu1", "password": "GoodPass123", "company": self.c1.id}
        self.assertEqual(c.post("/api/admin/users/", {**base, "role": "pilot"}, format="json").status_code, 400)
        r = c.post("/api/admin/users/", {**base, "role": "admin", "phone": "9876543210"}, format="json")
        self.assertEqual(r.status_code, 400)
        r = c.post("/api/admin/users/", {**base, "role": "dealer", "phone": "abc"}, format="json")
        self.assertEqual(r.status_code, 400)
        r = c.post("/api/admin/users/", {**base, "role": "dealer", "phone": "9876543210"}, format="json")
        self.assertEqual(r.status_code, 201, r.content)

    def test_role_cannot_change(self):
        r = self.admin().patch(f"/api/admin/users/{self.dealer1.pk}/", {"role": "pilot"}, format="json")
        self.assertEqual(r.status_code, 400)
        self.dealer1.refresh_from_db()
        self.assertEqual(self.dealer1.role, "dealer")

    def test_admin_resets_password_without_old_one(self):
        c, r = self.login("dealer1", "OwnPass1234")
        c.credentials(HTTP_AUTHORIZATION="Bearer " + r.data["access"])
        r = self.admin().patch(f"/api/admin/users/{self.dealer1.pk}/", {"password": "BrandNew123"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertEqual(c.get("/api/auth/me").status_code, 401)          # signed out everywhere
        _, r = self.login("dealer1", "BrandNew123")
        self.assertEqual(r.status_code, 200)
        r = self.admin().patch(f"/api/admin/users/{self.dealer1.pk}/", {"password": "short"}, format="json")
        self.assertEqual(r.status_code, 400)
