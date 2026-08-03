from django.contrib import admin

from .models import (Device, Driver, DriverAttendance, Geofence, GeofenceEvent,
                     Telemetry, Trip, Vehicle, VehicleDocument)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("device_id", "company", "online", "last_seen", "last_ip")
    list_filter = ("online", "company")
    search_fields = ("device_id", "label", "sim_number")


class VehicleDocumentInline(admin.TabularInline):
    model = VehicleDocument
    extra = 0


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("registration_number", "company", "status", "device", "active_driver")
    list_filter = ("status", "company")
    search_fields = ("registration_number", "make", "model")
    inlines = [VehicleDocumentInline]


@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "doc_type", "number", "expiry_date")
    list_filter = ("doc_type",)
    search_fields = ("vehicle__registration_number", "number")


class DriverAttendanceInline(admin.TabularInline):
    model = DriverAttendance
    extra = 0


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "phone", "license_no", "monthly_salary")
    search_fields = ("name", "phone", "license_no")
    inlines = [DriverAttendanceInline]


@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    list_display = ("device", "vehicle", "received_at", "speed_kmph", "total_litres", "has_gps_fix")
    list_filter = ("has_gps_fix", "device")
    date_hierarchy = "received_at"


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "status", "started_at", "ended_at", "distance_km", "max_speed_kmph")
    list_filter = ("status",)


@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "kind", "purpose", "active")
    list_filter = ("kind", "purpose", "active", "company")


@admin.register(GeofenceEvent)
class GeofenceEventAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "geofence", "event", "ts")
    list_filter = ("event",)
