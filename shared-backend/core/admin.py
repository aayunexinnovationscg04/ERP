from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import (Company, CompanySettings, RolePermission, User,
                     UserModuleOverride)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "status", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("status",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "role", "company", "email", "is_staff")
    list_filter = ("role", "company", "is_staff", "is_superuser")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Fuel Guard X", {"fields": ("company", "role", "phone")}),
    )


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ("company", "overspeed_limit_kmph", "offline_after_seconds",
                     "theft_drop_litres", "low_fuel_litres", "max_idle_minutes")


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ("role", "module", "allowed")
    list_filter = ("role", "allowed")


@admin.register(UserModuleOverride)
class UserModuleOverrideAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "allowed")
    list_filter = ("allowed",)
