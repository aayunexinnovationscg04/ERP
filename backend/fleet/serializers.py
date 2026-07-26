from rest_framework import serializers

from .models import Device, Driver, Geofence, Telemetry, Trip, Vehicle


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


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ["id", "name", "phone", "license_no"]


class _LatestMixin:
    def get_latest(self, obj):
        t = obj.telemetry.order_by("-received_at").first()
        return TelemetrySerializer(t).data if t else None


class VehicleListSerializer(_LatestMixin, serializers.ModelSerializer):
    device_id = serializers.CharField(source="device.device_id", read_only=True, default=None)
    driver_name = serializers.CharField(source="active_driver.name", read_only=True, default=None)
    latest = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ["id", "registration_number", "status", "make", "model",
                  "device_id", "driver_name", "latest"]


class VehicleDetailSerializer(_LatestMixin, serializers.ModelSerializer):
    device = DeviceSerializer(read_only=True)
    active_driver = DriverSerializer(read_only=True)
    latest = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = ["id", "registration_number", "status", "make", "model",
                  "tank_capacity_litres", "device", "active_driver", "latest",
                  "created_at"]


class TripSerializer(serializers.ModelSerializer):
    vehicle_reg = serializers.CharField(source="vehicle.registration_number", read_only=True)

    class Meta:
        model = Trip
        fields = ["id", "vehicle", "vehicle_reg", "driver", "started_at", "ended_at",
                  "start_lat", "start_lng", "end_lat", "end_lng", "distance_km",
                  "max_speed_kmph", "avg_speed_kmph", "fuel_consumed_litres", "status"]


class GeofenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Geofence
        fields = ["id", "name", "kind", "center_lat", "center_lng", "radius_m",
                  "polygon", "purpose", "active", "created_at"]
        read_only_fields = ["created_at"]
