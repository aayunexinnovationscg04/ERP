"""Canonical registry of accessible modules / tabs across the three ERPs.

Role Management (Admin) toggles which of these each role can see, globally.
Per-user overrides can then grant/deny individual modules for one member.

`key` is stable (stored in DB + sent to frontends); `label`/`group` are for UI.
"""

MODULES = [
    # --- Dealer / Company ERP ---
    {"key": "dashboard", "label": "Dashboard", "group": "Dealer"},
    {"key": "fleet", "label": "Fleet", "group": "Dealer"},
    {"key": "live_map", "label": "Live Map", "group": "Dealer"},
    {"key": "trips", "label": "Trips", "group": "Dealer"},
    {"key": "fuel", "label": "Fuel Monitoring", "group": "Dealer"},
    {"key": "drivers", "label": "Pilots", "group": "Dealer"},
    {"key": "alerts", "label": "Alerts", "group": "Dealer"},
    {"key": "geofences", "label": "Geofences", "group": "Dealer"},
    {"key": "billing", "label": "Billing & ERP", "group": "Dealer"},
    {"key": "reports", "label": "Reports", "group": "Dealer"},
    # --- Pilot ERP ---
    {"key": "driver_home", "label": "My Vehicle", "group": "Pilot"},
    {"key": "driver_trips", "label": "My Trips", "group": "Pilot"},
    {"key": "driver_alerts", "label": "My Alerts", "group": "Pilot"},
    # --- Admin ERP ---
    {"key": "companies", "label": "Companies", "group": "Admin"},
    {"key": "users", "label": "User Management", "group": "Admin"},
    {"key": "roles", "label": "Role Management", "group": "Admin"},
    {"key": "devices", "label": "Device Management", "group": "Admin"},
    {"key": "platform", "label": "Platform Health", "group": "Admin"},
]

MODULE_KEYS = [m["key"] for m in MODULES]

# Sensible starting defaults per role (Admin editable via Role Management).
# Admin is always all-access and is NOT listed here (cannot be locked out).
DEFAULT_ACCESS = {
    "dealer": ["dashboard", "fleet", "live_map", "trips", "fuel", "drivers",
               "alerts", "geofences", "billing", "reports"],
    "manager": ["dashboard", "fleet", "live_map", "trips", "fuel", "drivers",
                "alerts", "geofences", "reports"],
    "pilot": ["driver_home", "driver_trips", "driver_alerts"],
}
