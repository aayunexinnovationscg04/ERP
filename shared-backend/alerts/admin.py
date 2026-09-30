from django.contrib import admin

from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("type", "severity", "status", "vehicle", "device", "created_at")
    list_filter = ("type", "severity", "status", "company")
    date_hierarchy = "created_at"
    search_fields = ("title", "message")
