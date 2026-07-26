from django.contrib import admin

from .models import Command


@admin.register(Command)
class CommandAdmin(admin.ModelAdmin):
    list_display = ("payload", "device", "status", "created_at", "delivered_at")
    list_filter = ("status", "payload")
