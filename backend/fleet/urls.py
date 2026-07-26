from rest_framework.routers import DefaultRouter

from .views import (DashboardViewSet, DeviceViewSet, GeofenceViewSet,
                    TripViewSet, VehicleViewSet)

router = DefaultRouter()
router.register("vehicles", VehicleViewSet, basename="vehicle")
router.register("trips", TripViewSet, basename="trip")
router.register("devices", DeviceViewSet, basename="device")
router.register("geofences", GeofenceViewSet, basename="geofence")
router.register("dashboard/summary", DashboardViewSet, basename="dashboard")

urlpatterns = router.urls
