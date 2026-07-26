from rest_framework import serializers

from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    vehicle_reg = serializers.CharField(source="vehicle.registration_number",
                                        read_only=True, default=None)
    device_id = serializers.CharField(source="device.device_id",
                                      read_only=True, default=None)

    class Meta:
        model = Alert
        fields = ["id", "type", "severity", "status", "title", "message",
                  "lat", "lng", "meta", "vehicle", "vehicle_reg", "device",
                  "device_id", "created_at", "acknowledged_at"]
