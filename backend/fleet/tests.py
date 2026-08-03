"""Core derivation tests. Run: .venv/bin/python manage.py test fleet"""

from django.test import TestCase
from django.utils import timezone

from alerts.models import Alert
from core.models import Company, CompanySettings
from fleet.derivation import mark_offline, process_telemetry
from fleet.geo import haversine_km, point_in_geofence
from fleet.models import Device, Geofence, Telemetry, Trip, Vehicle


class GeoTests(TestCase):
    def test_haversine_known_distance(self):
        # ~1.11 km per 0.01 deg latitude
        d = haversine_km(21.10, 81.66, 21.11, 81.66)
        self.assertAlmostEqual(d, 1.11, delta=0.05)

    def test_point_in_circle(self):
        gf = Geofence(kind=Geofence.Kind.CIRCLE, center_lat=21.10, center_lng=81.66, radius_m=500)
        self.assertTrue(point_in_geofence(21.101, 81.66, gf))
        self.assertFalse(point_in_geofence(21.20, 81.66, gf))


class DerivationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="T", slug="t")
        CompanySettings.objects.create(company=self.company, overspeed_limit_kmph=60)
        self.device = Device.objects.create(device_id="d1", company=self.company)
        self.vehicle = Vehicle.objects.create(
            company=self.company, registration_number="R1", device=self.device)

    def _emit(self, received_at=None, **fields):
        f = dict(has_gps_fix=True, latitude=21.1, longitude=81.6, recording=True)
        f.update(fields)
        t = Telemetry.objects.create(device=self.device, vehicle=self.vehicle, **f)
        if received_at is not None:
            # received_at is auto_now_add=True, which ignores any value passed to
            # create() on INSERT -- patch it with a real UPDATE instead.
            Telemetry.objects.filter(pk=t.pk).update(received_at=received_at)
            t.refresh_from_db()
        process_telemetry(t)
        return t

    def test_overspeed_rising_edge_only(self):
        self._emit(speed_kmph=40)
        self._emit(speed_kmph=72)   # edge -> alert
        self._emit(speed_kmph=80)   # still over -> no new alert
        self.assertEqual(Alert.objects.filter(type=Alert.Type.OVERSPEED).count(), 1)

    def test_trip_opens_and_closes(self):
        # Real device pings land ~60-100s apart (see PHASE1_SPEC); space these the same
        # way so the GPS-jitter plausibility guard in _accumulate_trip doesn't reject a
        # perfectly normal ~1.1km hop as an impossible-speed outlier.
        now = timezone.now()
        self._emit(speed_kmph=30, latitude=21.10, longitude=81.60, received_at=now)
        self._emit(speed_kmph=30, latitude=21.11, longitude=81.60,
                   received_at=now + timezone.timedelta(seconds=90))
        self.assertEqual(Trip.objects.filter(status="active").count(), 1)
        self._emit(speed_kmph=0, recording=False,
                   received_at=now + timezone.timedelta(seconds=180))  # recording off closes trip
        self.assertEqual(Trip.objects.filter(status="active").count(), 0)
        trip = Trip.objects.first()
        self.assertGreater(trip.distance_km, 0.9)   # ~1.1 km travelled

    def test_tamper_on_lock_open(self):
        self._emit(lock_active=True)
        self._emit(lock_active=False)   # True -> False = opened
        self.assertEqual(Alert.objects.filter(type=Alert.Type.TAMPER).count(), 1)

    def test_geofence_breach_on_restricted_enter(self):
        Geofence.objects.create(company=self.company, name="R", kind=Geofence.Kind.CIRCLE,
                                center_lat=21.11, center_lng=81.60, radius_m=300,
                                purpose=Geofence.Purpose.RESTRICTED)
        self._emit(latitude=21.20, longitude=81.60)   # outside
        self._emit(latitude=21.11, longitude=81.60)   # enter restricted -> breach
        self.assertEqual(Alert.objects.filter(type=Alert.Type.GEOFENCE_BREACH).count(), 1)

    def test_offline_sweep(self):
        self._emit(speed_kmph=10)
        # backdate last_seen far beyond the window
        Device.objects.filter(pk=self.device.pk).update(
            last_seen=timezone.now() - timezone.timedelta(hours=1), online=True)
        n = mark_offline()
        self.assertEqual(n, 1)
        self.assertEqual(Alert.objects.filter(type=Alert.Type.DEVICE_OFFLINE).count(), 1)
