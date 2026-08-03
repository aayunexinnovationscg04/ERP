from datetime import timedelta

from django.db.models import Case, IntegerField, Sum, Value, When
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import (CanWriteOrReadOnly, CompanyScopedQuerysetMixin,
                              IsDealerOrAdmin)
from ingest.models import Command

from .models import Device, Pilot, Geofence, Telemetry, Trip, Vehicle
from .serializers import (DeviceSerializer, PilotDetailSerializer,
                          PilotListSerializer, GeofenceSerializer,
                          TelemetrySerializer, TripSerializer,
                          VehicleDetailSerializer, VehicleListSerializer)

MAX_HISTORY = 5000
STATUS_VALUES = [c[0] for c in Vehicle.Status.choices]


class VehicleViewSet(CompanyScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsDealerOrAdmin]

    def get_queryset(self):
        qs = self.scoped(
            Vehicle.objects.select_related("device", "active_pilot")
                           .prefetch_related("documents")
        )
        # ?priority_status=active|idle|offline|maintenance sorts that status to the
        # top; the client only tracks *which* status is prioritised (for the arrow
        # icon) and re-requests — the actual row ordering happens here, in the DB.
        priority = self.request.query_params.get("priority_status")
        if priority in STATUS_VALUES:
            qs = qs.annotate(
                _priority=Case(
                    When(status=priority, then=Value(0)),
                    default=Value(1), output_field=IntegerField(),
                )
            ).order_by("_priority", "registration_number")
        else:
            qs = qs.order_by("registration_number")
        return qs

    def get_serializer_class(self):
        return VehicleDetailSerializer if self.action == "retrieve" else VehicleListSerializer

    @action(detail=True, methods=["patch"], permission_classes=[IsDealerOrAdmin, CanWriteOrReadOnly])
    def local_name(self, request, pk=None):
        """The only writable field on this otherwise read-only viewset — a
        dealer-facing nickname, separate from the write-gating on everything
        else fleet-related (which has no create/update UI at all yet)."""
        vehicle = self.get_object()
        name = (request.data.get("local_name") or "").strip()
        if not name:
            return Response({"error": "local_name is required"}, status=400)
        if len(name) > 10:
            return Response({"error": "local_name must be 10 characters or fewer"}, status=400)
        vehicle.local_name = name
        vehicle.save(update_fields=["local_name"])
        return Response({"id": vehicle.id, "local_name": vehicle.local_name})

    @action(detail=True)
    def telemetry(self, request, pk=None):
        """Route history for the map. ?from=ISO&to=ISO&limit=N (fixed points only)."""
        vehicle = self.get_object()
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

    @action(detail=True)
    def trips(self, request, pk=None):
        vehicle = self.get_object()
        qs = Trip.objects.filter(vehicle=vehicle).order_by("-started_at")[:200]
        return Response(TripSerializer(qs, many=True).data)


class TripViewSet(CompanyScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsDealerOrAdmin]
    serializer_class = TripSerializer
    company_field = "vehicle__company"

    def get_queryset(self):
        return self.scoped(Trip.objects.select_related("vehicle"))


class DeviceViewSet(CompanyScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    # read for dealers/managers; the `command` write action needs may_write
    permission_classes = [IsDealerOrAdmin, CanWriteOrReadOnly]
    serializer_class = DeviceSerializer

    def get_queryset(self):
        return self.scoped(Device.objects.all())

    @action(detail=True, methods=["post"])
    def command(self, request, pk=None):
        """Queue a command (e.g. 'open') for delivery on the device's next POST."""
        device = self.get_object()
        payload = (request.data or {}).get("payload")
        if not payload:
            return Response({"error": "payload is required"}, status=400)
        cmd = Command.objects.create(device=device, payload=str(payload))
        return Response({"ok": True, "command_id": cmd.id, "status": cmd.status}, status=201)


class GeofenceViewSet(CompanyScopedQuerysetMixin, viewsets.ModelViewSet):
    # read for dealers/managers; create/update/delete need may_write
    permission_classes = [IsDealerOrAdmin, CanWriteOrReadOnly]
    serializer_class = GeofenceSerializer

    def get_queryset(self):
        return self.scoped(Geofence.objects.all())

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.company)


class DashboardViewSet(CompanyScopedQuerysetMixin, viewsets.ViewSet):
    permission_classes = [IsDealerOrAdmin]

    def list(self, request):
        vehicles = self.scoped(Vehicle.objects.all())
        by_status = {s: 0 for s in ("active", "idle", "offline", "maintenance")}
        for v in vehicles.values("status"):
            by_status[v["status"]] = by_status.get(v["status"], 0) + 1

        devices = self.scoped(Device.objects.all())
        online = devices.filter(online=True).count()

        from alerts.models import Alert
        open_alerts = self.scoped(Alert.objects.all()).filter(status="open").count()

        since = timezone.now() - timedelta(hours=24)
        # trips are already company-scoped via vehicle membership
        trips_today = Trip.objects.filter(vehicle__in=vehicles, started_at__gte=since)
        agg = trips_today.aggregate(dist=Sum("distance_km"), fuel=Sum("fuel_consumed_litres"))

        return Response({
            "vehicles_total": vehicles.count(),
            "active": by_status["active"],
            "idle": by_status["idle"],
            "offline": by_status["offline"],
            "devices_online": online,
            "devices_total": devices.count(),
            "open_alerts": open_alerts,
            "distance_today_km": round(agg["dist"] or 0, 1),
            "fuel_today_litres": round(agg["fuel"] or 0, 1),
        })


class PilotViewSet(CompanyScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsDealerOrAdmin]

    def get_queryset(self):
        return self.scoped(
            Pilot.objects.prefetch_related("vehicles", "attendance")
        ).order_by("name")

    def get_serializer_class(self):
        return PilotDetailSerializer if self.action == "retrieve" else PilotListSerializer
