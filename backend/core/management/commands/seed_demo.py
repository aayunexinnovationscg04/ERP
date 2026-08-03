"""Seed a clearly-labelled demo company with vehicles, pilots, trips, alerts,
geofences and documents so the dealer and pilot ERPs have data to show in a
client demo. Safe to re-run (get_or_create everywhere); pass --reset to wipe
just this demo company first.

    .venv/bin/python manage.py seed_demo [--reset]
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from alerts.models import Alert
from core.models import Company, CompanySettings, User
from fleet.models import (Device, Pilot, PilotAttendance, Geofence,
                          Telemetry, Trip, Vehicle, VehicleDocument)

BASE_LAT, BASE_LNG = 21.1458, 79.0882  # generic demo depot location

PILOT_NAMES = ["Ramesh Kumar", "Suresh Yadav", "Vikram Singh", "Anil Sharma"]
VEHICLES = [
    ("MH31AB1234", "Tata", "407", Vehicle.Status.ACTIVE),
    ("MH31CD5678", "Ashok Leyland", "1616", Vehicle.Status.ACTIVE),
    ("MH31EF9012", "Mahindra", "Bolero Pickup", Vehicle.Status.IDLE),
    ("MH31GH3456", "Eicher", "Pro 2049", Vehicle.Status.OFFLINE),
]


class Command(BaseCommand):
    help = "Seed a demo company with vehicles, pilots, trips and alerts for client demos."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="delete existing demo-fleet company first")

    def handle(self, *args, **opts):
        if opts["reset"]:
            deleted, _ = Company.objects.filter(slug="demo-fleet").delete()
            self.stdout.write(f"reset: deleted {deleted} row(s)")

        with transaction.atomic():
            company = self._company()
            pilots = self._pilots(company)
            pilot_user = self._users(company, pilots)
            vehicles = self._vehicles(company, pilots)
            self._trips(vehicles, pilots)
            self._alerts(company, vehicles)
            self._geofences(company)
            self._documents(vehicles)

        self.stdout.write(self.style.SUCCESS(
            "\nDemo data ready.\n"
            "  Dealer ERP  ->  dealer / dealer123\n"
            "  Pilot  ERP  ->  pilot / pilot123\n"
        ))

    def _company(self):
        company, _ = Company.objects.get_or_create(
            slug="demo-fleet", defaults={"name": "Demo Fleet Co", "status": Company.Status.ACTIVE}
        )
        CompanySettings.objects.get_or_create(company=company)
        return company

    def _users(self, company, pilots):
        dealer, _ = User.objects.get_or_create(username="dealer", defaults={"company": company})
        dealer.company, dealer.role, dealer.can_edit = company, User.Role.DEALER, True
        dealer.set_password("dealer123")
        dealer.save()

        pilot_user, _ = User.objects.get_or_create(username="pilot", defaults={"company": company})
        pilot_user.company, pilot_user.role = company, User.Role.PILOT
        pilot_user.set_password("pilot123")
        pilot_user.save()

        pilots[0].user = pilot_user
        pilots[0].save(update_fields=["user"])
        return pilot_user

    def _pilots(self, company):
        pilots = []
        for i, name in enumerate(PILOT_NAMES):
            p, _ = Pilot.objects.get_or_create(
                company=company, name=name,
                defaults={
                    "phone": f"9876{500000 + i * 1111}",
                    "license_no": f"MH31{2018 + i}{100000 + i}",
                    "monthly_salary": Decimal(15000 + i * 1500),
                },
            )
            pilots.append(p)
        today = timezone.localdate()
        for p in pilots:
            for days_ago in range(14):
                date = today - timedelta(days=days_ago)
                status = random.choices(
                    [PilotAttendance.Status.PRESENT, PilotAttendance.Status.HALF_DAY,
                     PilotAttendance.Status.LEAVE, PilotAttendance.Status.ABSENT],
                    weights=[80, 10, 5, 5], k=1,
                )[0]
                PilotAttendance.objects.get_or_create(pilot=p, date=date, defaults={"status": status})
        return pilots

    def _vehicles(self, company, pilots):
        vehicles = []
        now = timezone.now()
        for i, (reg, make, model, status) in enumerate(VEHICLES):
            online = status != Vehicle.Status.OFFLINE
            device, _ = Device.objects.get_or_create(
                device_id=f"demo-esp32-{i + 1:02d}",
                defaults={"company": company, "label": f"Demo unit {i + 1}"},
            )
            device.company = company
            device.online = online
            device.last_seen = now - (timedelta(minutes=random.randint(1, 8)) if online else timedelta(hours=9))
            device.save()

            pilot = pilots[i % len(pilots)]
            vehicle, _ = Vehicle.objects.get_or_create(
                company=company, registration_number=reg,
                defaults={"make": make, "model": model, "tank_capacity_litres": 120},
            )
            vehicle.device = device
            vehicle.active_pilot = pilot
            vehicle.status = status
            vehicle.make, vehicle.model = make, model
            vehicle.save()
            vehicles.append(vehicle)

            lat = BASE_LAT + random.uniform(-0.05, 0.05)
            lng = BASE_LNG + random.uniform(-0.05, 0.05)
            Telemetry.objects.create(
                device=device, vehicle=vehicle,
                received_at=device.last_seen,
                latitude=lat, longitude=lng,
                speed_kmph=round(random.uniform(18, 58), 1) if status == Vehicle.Status.ACTIVE else 0,
                satellites=random.randint(6, 12), altitude_m=round(random.uniform(280, 320), 1),
                recording=status == Vehicle.Status.ACTIVE, lock_active=True,
                gsm_signal=random.randint(-95, -60), has_gps_fix=True, raw={},
            )
        return vehicles

    def _trips(self, vehicles, pilots):
        now = timezone.now()
        for vehicle in vehicles:
            if vehicle.status == Vehicle.Status.OFFLINE:
                continue  # a long-offline truck has no recent trips
            n_days = 7
            for day in range(n_days):
                if random.random() < 0.15:
                    continue  # skip a day here and there, like real usage
                start = now - timedelta(days=day, hours=random.randint(1, 10))
                dur_min = random.randint(25, 150)
                distance = round(dur_min / 60 * random.uniform(28, 48), 1)
                avg_speed = round(distance / (dur_min / 60), 1)
                max_speed = round(avg_speed + random.uniform(8, 25), 1)
                fuel = round(distance * random.uniform(0.09, 0.14), 1)
                lat0 = BASE_LAT + random.uniform(-0.05, 0.05)
                lng0 = BASE_LNG + random.uniform(-0.05, 0.05)
                lat1 = BASE_LAT + random.uniform(-0.05, 0.05)
                lng1 = BASE_LNG + random.uniform(-0.05, 0.05)
                Trip.objects.get_or_create(
                    vehicle=vehicle, started_at=start,
                    defaults={
                        "pilot": vehicle.active_pilot,
                        "ended_at": start + timedelta(minutes=dur_min),
                        "start_lat": lat0, "start_lng": lng0,
                        "end_lat": lat1, "end_lng": lng1,
                        "distance_km": distance, "max_speed_kmph": max_speed,
                        "avg_speed_kmph": avg_speed, "fuel_consumed_litres": fuel,
                        "status": Trip.Status.COMPLETED,
                    },
                )
            # one trip that started within the last few hours so "today" KPIs aren't zero
            start = now - timedelta(hours=random.uniform(0.5, 3))
            dur_min = random.randint(20, 70)
            distance = round(dur_min / 60 * random.uniform(28, 45), 1)
            Trip.objects.get_or_create(
                vehicle=vehicle, started_at=start,
                defaults={
                    "pilot": vehicle.active_pilot,
                    "ended_at": start + timedelta(minutes=dur_min) if vehicle.status != Vehicle.Status.ACTIVE else None,
                    "distance_km": distance,
                    "max_speed_kmph": round(random.uniform(40, 70), 1),
                    "avg_speed_kmph": round(random.uniform(25, 45), 1),
                    "fuel_consumed_litres": round(distance * 0.11, 1),
                    "status": Trip.Status.COMPLETED if vehicle.status != Vehicle.Status.ACTIVE else Trip.Status.ACTIVE,
                },
            )

    def _alerts(self, company, vehicles):
        now = timezone.now()
        specs = [
            (Alert.Type.OVERSPEED, Alert.Severity.WARNING, "Overspeed: 78 km/h",
             "exceeded 60 km/h on the highway stretch.", Alert.Status.OPEN, 2),
            (Alert.Type.GEOFENCE_BREACH, Alert.Severity.WARNING, "Geofence exit: Warehouse Yard",
             "left the allowed zone 'Warehouse Yard'.", Alert.Status.ACKNOWLEDGED, 20),
            (Alert.Type.TAMPER, Alert.Severity.CRITICAL, "Lock opened",
             "fuel lock was opened outside a scheduled stop.", Alert.Status.OPEN, 5),
            (Alert.Type.IDLE_TOO_LONG, Alert.Severity.WARNING, "Idle too long",
             "has been stopped (engine idle) for over 45 minutes.", Alert.Status.RESOLVED, 40),
            (Alert.Type.DEVICE_OFFLINE, Alert.Severity.WARNING, "Device offline",
             "tracker has not reported in over 15 minutes.", Alert.Status.OPEN, 9),
            (Alert.Type.FUEL_FILL, Alert.Severity.INFO, "Fuel fill: +42.0 L",
             "refuelled 42.0 L at the depot.", Alert.Status.RESOLVED, 26),
            (Alert.Type.LOW_FUEL, Alert.Severity.WARNING, "Low fuel", "fuel level is below the configured threshold.",
             Alert.Status.OPEN, 12),
            (Alert.Type.FUEL_THEFT, Alert.Severity.CRITICAL, "Possible fuel theft: -18.0 L",
             "lost 18.0 L suddenly while parked overnight.", Alert.Status.ACKNOWLEDGED, 55),
        ]
        for i, (type_, sev, title, msg, status, hours_ago) in enumerate(specs):
            vehicle = vehicles[i % len(vehicles)]
            created_at = now - timedelta(hours=hours_ago)
            alert, created = Alert.objects.get_or_create(
                company=company, vehicle=vehicle, type=type_, title=title,
                defaults={
                    "severity": sev,
                    "message": f"{vehicle.registration_number} {msg}",
                    "status": status,
                    "lat": BASE_LAT + random.uniform(-0.05, 0.05),
                    "lng": BASE_LNG + random.uniform(-0.05, 0.05),
                },
            )
            if created:
                Alert.objects.filter(pk=alert.pk).update(created_at=created_at)

    def _geofences(self, company):
        Geofence.objects.get_or_create(
            company=company, name="Warehouse Yard",
            defaults={"kind": Geofence.Kind.CIRCLE, "center_lat": BASE_LAT, "center_lng": BASE_LNG,
                      "radius_m": 400, "purpose": Geofence.Purpose.ALLOWED},
        )
        Geofence.objects.get_or_create(
            company=company, name="Old City Restricted Zone",
            defaults={"kind": Geofence.Kind.CIRCLE, "center_lat": BASE_LAT + 0.045, "center_lng": BASE_LNG + 0.03,
                      "radius_m": 700, "purpose": Geofence.Purpose.RESTRICTED},
        )
        Geofence.objects.get_or_create(
            company=company, name="Customer Site - North Depot",
            defaults={"kind": Geofence.Kind.CIRCLE, "center_lat": BASE_LAT - 0.03, "center_lng": BASE_LNG + 0.04,
                      "radius_m": 300, "purpose": Geofence.Purpose.CUSTOMER_SITE},
        )

    def _documents(self, vehicles):
        today = timezone.localdate()
        doc_plan = [
            (VehicleDocument.DocType.RC, 400),
            (VehicleDocument.DocType.INSURANCE, 20),   # expiring soon, on purpose
            (VehicleDocument.DocType.PERMIT, 200),
            (VehicleDocument.DocType.PUC, -10),         # already expired, on purpose
            (VehicleDocument.DocType.FITNESS, 150),
        ]
        for vi, vehicle in enumerate(vehicles):
            for di, (doc_type, days_offset) in enumerate(doc_plan):
                VehicleDocument.objects.get_or_create(
                    vehicle=vehicle, doc_type=doc_type,
                    defaults={
                        "number": f"{doc_type.upper()}-{vi + 1}{di + 1}0{vi}{di}",
                        "expiry_date": today + timedelta(days=days_offset),
                    },
                )
