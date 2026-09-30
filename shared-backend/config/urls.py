"""URL configuration for Fuel Guard X."""

from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"ok": True, "service": "fuelguardx-api"})

urlpatterns = [
    # Django admin panel moved off /admin/ so the Admin Vue ERP can live at /admin/.
    path("django-admin/", admin.site.urls),
    path("api/health", health, name="health"),
    # device ingest (firmware-compatible)
    path("api/", include("ingest.urls")),
    # ERP REST API
    path("api/", include("core.urls")),
    path("api/", include("fleet.urls")),
    path("api/", include("alerts.urls")),
]
