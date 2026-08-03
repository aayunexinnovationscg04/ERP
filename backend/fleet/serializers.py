from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import (Device, Pilot, PilotAttendance, Geofence, Telemetry,
                     Trip, Vehicle, VehicleDocument)

EXPIRY_WARNING_DAYS = 30


class TelemetrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Telemetry
        fields = ["id", "received_at", "latitude", "longitude", "speed_kmph",
                  "satellites", "altitude_m", "flow_rate_lpm", "total_litres",
                  "recording", "lock_active", "gsm_signal", "has_gps_fix"]


class DeviceSerializer(serializers.ModelSerializer):
    pending_commands = serializers.SerializerMethodField()

    class Meta:
        model = Device
        fields = ["id", "device_id", "label", "sim_number", "firmware_version",
                  "online", "last_seen", "last_ip", "pending_commands"]

    def get_pending_commands(self, obj):
        return obj.commands.filter(status="queued").count()


class PilotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pilot
        fields = ["id", "name", "phone", "license_no"]


class PilotAttendanceSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = PilotAttendance
        fields = ["id", "date", "status", "status_label", "notes"]


class _AssignedVehicleMixin:
    """A pilot isn't tied to one vehicle by a direct FK — it's the reverse of
    Vehicle.active_pilot. `.vehicles.first()` needs an actual method call, so
    this has to be a SerializerMethodField (a dotted `source=` string only does
    attribute access, it can't call `.first()`)."""

    def get_assigned_vehicle(self, obj):
        v = obj.vehicles.first()
        if not v:
            return None
        return {"id": v.id, "registration_number": v.registration_number, "local_name": v.local_name}


class PilotListSerializer(_AssignedVehicleMixin, serializers.ModelSerializer):
    """Powers the Pilots page — the assigned vehicle rides along (entered via
    Django Admin only, same pattern as monthly_salary/attendance) so the boxes
    grid needs no extra request per pilot."""
    assigned_vehicle = serializers.SerializerMethodField()

    class Meta:
        model = Pilot
        fields = ["id", "name", "phone", "license_no", "assigned_vehicle"]


class PilotDetailSerializer(_AssignedVehicleMixin, serializers.ModelSerializer):
    attendance = PilotAttendanceSerializer(many=True, read_only=True)
    assigned_vehicle = serializers.SerializerMethodField()

    class Meta:
        model = Pilot
        fields = ["id", "name", "phone", "license_no", "monthly_salary",
                  "assigned_vehicle", "attendance"]


class VehicleDocumentSerializer(serializers.ModelSerializer):
    doc_type_label = serializers.CharField(source="get_doc_type_display", read_only=True)
    expiry_status = serializers.SerializerMethodField()

    class Meta:
        model = VehicleDocument
        fields = ["id", "doc_type", "doc_type_label", "number", "expiry_date",
                  "notes", "expiry_status"]

    def get_expiry_status(self, obj):
        """Computed here (not in the frontend) so every client agrees on what
        counts as 'expiring soon' without duplicating the date math."""
        if not obj.expiry_date:
            return "unknown"
        days_left = (obj.expiry_date - timezone.localdate()).days
        if days_left < 0:
            return "expired"
        if days_left <= EXPIRY_WARNING_DAYS:
            return "expiring_soon"
        return "valid"


class _LatestMixin:
    def get_latest(self, obj):
        t = obj.telemetry.order_by("-received_at").first()
        return TelemetrySerializer(t).data if t else None


class VehicleListSerializer(_LatestMixin, serializers.ModelSerializer):
    """Powers the Fleet table, including its per-row expand panel — carries
    pilot + documents up front so expanding a row needs no extra request."""
    device_id = serializers.CharField(source="device.device_id", read_only=True, default=None)
    pilot_name = serializers.CharField(source="active_pilot.name", read_only=True, default=None)
    active_pilot = PilotSerializer(read_only=True)
    documents = VehicleDocumentSerializer(many=True, read_only=True)
    latest = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ["id", "registration_number", "local_name", "status", "make", "model",
                  "tank_capacity_litres", "device_id", "pilot_name",
                  "active_pilot", "documents", "latest"]


class VehicleDetailSerializer(_LatestMixin, serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    active_pilot = PilotSerializer(read_only=True)
    documents = VehicleDocumentSerializer(many=True, read_only=True)
    latest = serializers.SerializerMethodField()
    latest_raw = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ["id", "registration_number", "local_name", "status", "make", "model",
                  "tank_capacity_litres", "device", "active_pilot", "documents",
                  "latest", "latest_raw", "created_at"]

    def get_latest_raw(self, obj):
        """The exact JSON the device's own POST carried, straight from the receiver
        bridge (see fleet.management.commands.sync_receiver) — identified purely by
        device_id, never by IP. Kept separate from `latest` so the Fleet table (which
        uses the same _LatestMixin) never has to pull this JSONB blob for every row."""
        t = obj.telemetry.order_by("-received_at").first()
        return t.raw if t else None


class TripSerializer(serializers.ModelSerializer):
    vehicle_reg = serializers.CharField(source="vehicle.registration_number", read_only=True)

    class Meta:
        model = Trip
        fields = ["id", "vehicle", "vehicle_reg", "pilot", "started_at", "ended_at",
                  "start_lat", "start_lng", "end_lat", "end_lng", "distance_km",
                  "max_speed_kmph", "avg_speed_kmph", "fuel_consumed_litres", "status"]


class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = ["id", "name", "kind", "center_lat", "center_lng", "radius_m",
                  "polygon", "purpose", "active", "created_at"]
        read_only_fields = ["created_at"]
