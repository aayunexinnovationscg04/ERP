from django.urls import path
from rest_framework.routers import DefaultRouter

from .pilot_views import (PilotAlertsView, PilotSummaryView,
                          PilotTelemetryView, PilotTripsView,
                          PilotVehicleView)
from .views import (DashboardViewSet, DeviceViewSet, PilotViewSet,
                    GeofenceViewSet, TripViewSet, VehicleViewSet)

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("trips", TripViewSet, basename="trip")
router.register("devices", DeviceViewSet, basename="device")
router.register("geofences", GeofenceViewSet, basename="geofence")
router.register("pilots", PilotViewSet, basename="pilot")
router.register("dashboard/summary", DashboardViewSet, basename="dashboard")

urlpatterns = router.urls + [
    # Pilot ERP (self-scoped; role=PILOT only)
    path("pilot/summary", PilotSummaryView.as_view()),
    path("pilot/vehicle", PilotVehicleView.as_view()),
    path("pilot/vehicle/telemetry", PilotTelemetryView.as_view()),
    path("pilot/trips", PilotTripsView.as_view()),
    path("pilot/alerts", PilotAlertsView.as_view()),
]
