from rest_framework import serializers

from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    type_label = serializers.CharField(source="get_type_display", read_only=True)
    vehicle_reg = serializers.CharField(source="vehicle.registration_number",
                                        read_only=True, default=None)
    device_id = serializers.CharField(source="device.device_id",
                                      read_only=True, default=None)
    acknowledged_by_username = serializers.CharField(source="acknowledged_by.username",
                                                      read_only=True, default=None)

    class Meta:
        model = Alert
        fields = ["id", "type", "type_label", "severity", "status", "title", "message",
                  "lat", "lng", "meta", "vehicle", "vehicle_reg", "device",
                  "device_id", "created_at", "acknowledged_at",
                  "acknowledged_by_username"]
