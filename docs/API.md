# Fuel Guard X — Backend API (Phase 1)

Base URL (through nginx): `http://<host>:8090`  ·  Django direct: `http://127.0.0.1:8000`
All ERP endpoints require `Authorization: Bearer <access token>` unless noted.

## Auth
Access token (10 min) in the JSON body, kept in SPA memory only. Refresh token in an
HttpOnly `Secure` `SameSite=Strict` cookie `fgx_rt_<portal>` (path `/api/auth/`), rotated
on every refresh; a reused refresh token is rejected. All `/api/auth/*` POSTs need header
`X-FGX-Portal: admin|dealer|pilot`; an account may only sign in to its role's portal
(admin → admin, dealer/manager → dealer, pilot → pilot). Refresh lifetime: admin 12 h hard
cap; dealer/pilot 7 days idle, 30 days max. Changing a user's password, role, company or
active flag revokes all their tokens instantly. Details: `backend/core/tokens.py`.

| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/auth/login` | `{username, password}` | → `{access, access_expires_in, user}` + sets refresh cookie; 401 bad creds, 403 wrong portal |
| POST | `/api/auth/refresh` | — (cookie) | → `{access, access_expires_in, user}` + rotated cookie; 401 = sign in again |
| POST | `/api/auth/logout` | — (cookie) | revokes this portal's refresh token, clears cookie → 204 |
| POST | `/api/auth/logout-all` | — (Bearer) | revokes every session of the user on all devices/portals → 204 |
| GET | `/api/auth/me` | — | current user + company |
| GET | `/api/health` | — | public health check |

## Fleet (owner/manager/superadmin, company-scoped)
| Method | Path | Notes |
|---|---|---|
| GET | `/api/dashboard/summary/` | counts: total/active/idle/offline, devices online, open alerts, distance & fuel today |
| GET | `/api/vehicles/` | list + latest telemetry snapshot per vehicle |
| GET | `/api/vehicles/{id}/` | detail (device, driver, latest) |
| GET | `/api/vehicles/{id}/telemetry/?from&to&limit` | route history (GPS-fixed points, chronological) |
| GET | `/api/vehicles/{id}/trips/` | trips for a vehicle |
| GET | `/api/trips/` · `/api/trips/{id}/` | trips |
| GET | `/api/devices/` · `/api/devices/{id}/` | devices + pending-command count |
| POST | `/api/devices/{id}/command/` | `{payload}` (e.g. `"open"`) → queues command |
| GET/POST/PUT/DELETE | `/api/geofences/` | geofence CRUD (circle or polygon) |
| GET | `/api/alerts/?status&type&vehicle` | alerts, filterable |
| POST | `/api/alerts/{id}/acknowledge/` | acknowledge an alert |

## Admin (role `admin` only)
| Method | Path | Notes |
|---|---|---|
| GET | `/api/admin/modules` | all tabs/modules (key, label, group) |
| GET/POST | `/api/admin/companies/` | company CRUD |
| GET/POST | `/api/admin/users/` | list / create users (username, password, role, company, phone) |
| PATCH | `/api/admin/users/{id}/` | update role / company / is_active / password |
| GET | `/api/admin/users/{id}/permissions/` | effective + role defaults + overrides |
| PUT | `/api/admin/users/{id}/permissions/` | `{overrides:{module: true/false/null}}` (null clears) |
| GET | `/api/admin/roles` | role × module access matrix |
| PUT | `/api/admin/roles` | `{role:{module: bool}}` — set global role defaults |

`GET /api/auth/me` (and login/refresh) return `modules: [...]` — the caller's **effective**
accessible tabs (per-user override > role default > built-in default; admin = all).

The API enforces the same list (`core.permissions.ModuleAccess`): each endpoint declares the
modules that need its data and the caller must have at least one, otherwise **403**.

| Endpoint | Needs any of |
|---|---|
| `/api/vehicles/…` | fleet, live_map, fuel, dashboard, trips, drivers |
| `/api/trips/…` | trips, fuel, fleet, reports |
| `/api/devices/…` | fleet |
| `/api/geofences/…` | geofences, live_map |
| `/api/dashboard/summary/` | dashboard |
| `/api/pilots/…` | drivers |
| `/api/alerts/…` | alerts, dashboard, fuel, drivers |
| `/api/pilot/summary`, `/vehicle`, `/vehicle/telemetry` | driver_home |
| `/api/pilot/trips` | driver_trips |
| `/api/pilot/alerts` | driver_alerts |

## Device ingest (firmware, token-auth — NOT JWT)
| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/api/telemetry` | `X-Auth: <INGEST_TOKEN>` (or `?auth=`) | permissive body; stores Telemetry, runs derivation, returns queued commands |

Reply: `{"ok": true, "device_id": "...", "received": <bytes>, "commands": [{id,payload,content_type,ts}]}`

## Derivation (runs on each ingest)
- **Trip**: `recording=true` opens/continues; `recording=false` or a gap > offline window closes it. Accrues distance (haversine, fixed points), max speed, fuel Δ; avg speed at close.
- **Overspeed**: `speed > company limit` (default 60), one alert per rising edge.
- **Geofence**: point-in-zone vs previous state → enter/exit event; breach alert on restricted-enter / allowed-exit.
- **Tamper**: `lock_active` True→False → critical "Lock opened".
- **Fuel** (inert while sensor=0): fill (Δ≥+1L), theft (Δ≤−threshold), low-fuel (if configured).
- **Offline**: `mark_offline` sweep (systemd timer, 2 min) flags silent devices + DEVICE_OFFLINE alert.

## Quick test
```bash
B=http://127.0.0.1:8090
TOK=$(curl -s -X POST $B/api/auth/login -H 'Content-Type: application/json' -H 'X-FGX-Portal: admin' \
      -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access"])')
curl -s $B/api/dashboard/summary/ -H "Authorization: Bearer $TOK"
curl -s -X POST $B/api/telemetry -H 'X-Auth: fuelguardx' -H 'X-Device-Id: esp32-01' \
     -d '{"device_id":"esp32-01","latitude":21.14,"longitude":81.66,"speed_kmph":72,"satellites":9,"recording":true,"lock_active":false}'
```
