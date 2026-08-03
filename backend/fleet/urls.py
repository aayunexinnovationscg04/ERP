from django.urls import path
from rest_framework.routers import DefaultRouter

from .driver_views import (DriverAlertsView, DriverSummaryView,
                           DriverTelemetryView, DriverTripsView,
                           DriverVehicleView)
from .views import (DashboardViewSet, DeviceViewSet, DriverViewSet,
                    GeofenceViewSet, TripViewSet, VehicleViewSet)

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("trips", TripViewSet, basename="trip")
router.register("devices", DeviceViewSet, basename="device")
router.register("geofences", GeofenceViewSet, basename="geofence")
router.register("drivers", DriverViewSet, basename="driver")
router.register("dashboard/summary", DashboardViewSet, basename="dashboard")

urlpatterns = router.urls + [
    # Driver ERP (self-scoped; role=DRIVER only)
    path("driver/summary", DriverSummaryView.as_view()),
    path("driver/vehicle", DriverVehicleView.as_view()),
    path("driver/vehicle/telemetry", DriverTelemetryView.as_view()),
    path("driver/trips", DriverTripsView.as_view()),
    path("driver/alerts", DriverAlertsView.as_view()),
]
