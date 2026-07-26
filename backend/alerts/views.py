from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import (CanWriteOrReadOnly, CompanyScopedQuerysetMixin,
                              IsOwnerOrAdmin)

from .models import Alert
from .serializers import AlertSerializer


class AlertViewSet(CompanyScopedQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    # read for owners/managers; the `acknowledge` write action needs may_write
    permission_classes = [IsOwnerOrAdmin, CanWriteOrReadOnly]
    serializer_class = AlertSerializer

    def get_queryset(self):
        qs = self.scoped(Alert.objects.select_related("vehicle", "device"))
        params = self.request.query_params
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("type"):
            qs = qs.filter(type=params["type"])
        if params.get("vehicle"):
            qs = qs.filter(vehicle_id=params["vehicle"])
        return qs

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = Alert.Status.ACKNOWLEDGED
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.save(update_fields=["status", "acknowledged_by", "acknowledged_at"])
        return Response(AlertSerializer(alert).data)
