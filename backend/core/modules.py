"""Canonical registry of accessible modules / tabs across the three ERPs.

Role Management (Super Admin) toggles which of these each role can see, globally.
Per-user overrides can then grant/deny individual modules for one member.

`key` is stable (stored in DB + sent to frontends); `label`/`group` are for UI.
"""

MODULES = [
    # --- Owner / Company ERP ---
    {"key": "dashboard", "label": "Dashboard", "group": "Owner"},
    {"key": "fleet", "label": "Fleet", "group": "Owner"},
    {"key": "live_map", "label": "Live Map", "group": "Owner"},
    {"key": "trips", "label": "Trips", "group": "Owner"},
    {"key": "fuel", "label": "Fuel Monitoring", "group": "Owner"},
    {"key": "drivers", "label": "Drivers", "group": "Owner"},
    {"key": "alerts", "label": "Alerts", "group": "Owner"},
    {"key": "geofences", "label": "Geofences", "group": "Owner"},
    {"key": "billing", "label": "Billing & ERP", "group": "Owner"},
    {"key": "reports", "label": "Reports", "group": "Owner"},
    # --- Driver ERP ---
    {"key": "driver_home", "label": "My Vehicle", "group": "Driver"},
    {"key": "driver_trips", "label": "My Trips", "group": "Driver"},
    {"key": "driver_alerts", "label": "My Alerts", "group": "Driver"},
    # --- Super Admin ERP ---
    {"key": "companies", "label": "Companies", "group": "Admin"},
    {"key": "users", "label": "User Management", "group": "Admin"},
    {"key": "roles", "label": "Role Management", "group": "Admin"},
    {"key": "devices", "label": "Device Management", "group": "Admin"},
    {"key": "platform", "label": "Platform Health", "group": "Admin"},
]

MODULE_KEYS = [m["key"] for m in MODULES]

# Sensible starting defaults per role (Super Admin editable via Role Management).
# Super Admin is always all-access and is NOT listed here (cannot be locked out).
DEFAULT_ACCESS = {
    "owner": ["dashboard", "fleet", "live_map", "trips", "fuel", "drivers",
              "alerts", "geofences", "billing", "reports"],
    "manager": ["dashboard", "fleet", "live_map", "trips", "fuel", "drivers",
                "alerts", "geofences", "reports"],
    "driver": ["driver_home", "driver_trips", "driver_alerts"],
}
