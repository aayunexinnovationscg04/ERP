"""Driver ERP endpoints.

A driver only ever sees the ONE vehicle currently assigned to them
(Vehicle.active_driver -> Driver -> User). Every query below is derived from
request.user, so a driver can never reach another driver's or company's data.
"""

from datetime import timedelta

from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from alerts.models import Alert
from alerts.serializers import AlertSerializer
from core.permissions import IsDriver

from .models import Telemetry, Trip, Vehicle
from .serializers import TelemetrySerializer, TripSerializer, VehicleDetailSerializer

MAX_HISTORY = 5000


def driver_vehicle(user):
    """The vehicle assigned to this driver user, or None."""
    return (
        Vehicle.objects.filter(active_driver__user=user)
        .select_related("device", "active_driver")
        .first()
    )


class _DriverBase(APIView):
    permission_classes = [IsAuthenticated, IsDriver]

    def get_vehicle(self, request):
        return driver_vehicle(request.user)


class DriverVehicleView(_DriverBase):
    """GET /api/driver/vehicle — the driver's assigned vehicle + latest telemetry."""

    def get(self, request):
        vehicle = self.get_vehicle(request)
        if not vehicle:
            return Response({"detail": "No vehicle is assigned to you yet."}, status=404)
        return Response(VehicleDetailSerializer(vehicle).data)


class DriverTelemetryView(_DriverBase):
    """GET /api/driver/vehicle/telemetry?from&to&limit — route history (fixed points)."""

    def get(self, request):
        vehicle = self.get_vehicle(request)
        if not vehicle:
            return Response({"detail": "No vehicle assigned."}, status=404)
        qs = Telemetry.objects.filter(vehicle=vehicle, has_gps_fix=True)
        frm, to = request.query_params.get("from"), request.query_params.get("to")
        if frm:
            qs = qs.filter(received_at__gte=frm)
        if to:
            qs = qs.filter(received_at__lte=to)
        try:
            limit = min(int(request.query_params.get("limit", 1000)), MAX_HISTORY)
        except ValueError:
            limit = 1000
        qs = qs.order_by("received_at")[:limit]
        return Response(TelemetrySerializer(qs, many=True).data)


class DriverTripsView(_DriverBase):
    """GET /api/driver/trips — recent trips for the driver's vehicle."""

    def get(self, request):
        vehicle = self.get_vehicle(request)
        if not vehicle:
            return Response([])
        qs = Trip.objects.filter(vehicle=vehicle).order_by("-started_at")[:200]
        return Response(TripSerializer(qs, many=True).data)


class DriverAlertsView(_DriverBase):
    """GET /api/driver/alerts — alerts for the driver's vehicle (open + recent)."""

    def get(self, request):
        vehicle = self.get_vehicle(request)
        if not vehicle:
            return Response([])
        qs = Alert.objects.filter(vehicle=vehicle).select_related("vehicle", "device")
        if request.query_params.get("status"):
            qs = qs.filter(status=request.query_params["status"])
        return Response(AlertSerializer(qs.order_by("-created_at")[:200], many=True).data)


class DriverSummaryView(_DriverBase):
    """GET /api/driver/summary — compact status card for the driver home screen."""

    def get(self, request):
        vehicle = self.get_vehicle(request)
        if not vehicle:
            return Response({"assigned": False})

        latest = vehicle.telemetry.order_by("-received_at").first()
        active_trip = Trip.objects.filter(vehicle=vehicle, status=Trip.Status.ACTIVE).first()
        open_alerts = Alert.objects.filter(vehicle=vehicle, status="open").count()
        since = timezone.now() - timedelta(hours=24)
        today = Trip.objects.filter(vehicle=vehicle, started_at__gte=since)
        dist_today = sum(t.distance_km for t in today)

        return Response({
            "assigned": True,
            "vehicle": {
                "id": vehicle.id,
                "registration_number": vehicle.registration_number,
                "status": vehicle.status,
                "make": vehicle.make,
                "model": vehicle.model,
            },
            "latest": TelemetrySerializer(latest).data if latest else None,
            "on_trip": bool(active_trip),
            "active_trip_id": active_trip.id if active_trip else None,
            "open_alerts": open_alerts,
            "distance_today_km": round(dist_today, 1),
        })
