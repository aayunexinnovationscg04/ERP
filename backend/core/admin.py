from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Company, CompanySettings, User


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
    list_display = ("company", "overspeed_limit_kmph", "offline_after_seconds", "theft_drop_litres")
