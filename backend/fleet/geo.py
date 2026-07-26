"""Geospatial helpers — no external deps, plain math. Good enough for pilot scale."""

import math


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance in km between two lat/lng points."""
    if None in (lat1, lng1, lat2, lng2):
        return 0.0
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def point_in_geofence(lat, lng, geofence):
    """True if (lat,lng) is inside the geofence (circle or polygon)."""
    if lat is None or lng is None:
        return False
    if geofence.kind == geofence.Kind.CIRCLE:
        if geofence.center_lat is None or geofence.radius_m is None:
            return False
        dist_m = haversine_km(lat, lng, geofence.center_lat, geofence.center_lng) * 1000
        return dist_m <= geofence.radius_m
    # polygon: ray-casting. polygon is [[lat,lng], ...]
    poly = geofence.polygon or []
    if len(poly) < 3:
        return False
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        yi, xi = poly[i][0], poly[i][1]
        yj, xj = poly[j][0], poly[j][1]
        if ((yi > lat) != (yj > lat)) and (
            lng < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside
