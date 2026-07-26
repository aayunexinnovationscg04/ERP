# Fuel Guard X — Backend API (Phase 1)

Base URL (through nginx): `http://<host>:8090`  ·  Django direct: `http://127.0.0.1:8000`
All ERP endpoints require `Authorization: Bearer <access token>` unless noted.

## Auth
| Method | Path | Body | Notes |
|---|---|---|---|
| POST | `/api/auth/login` | `{username, password}` | → `{access, refresh, user}`; token carries role + company_id |
| POST | `/api/auth/refresh` | `{refresh}` | → `{access}` |
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
TOK=$(curl -s -X POST $B/api/auth/login -H 'Content-Type: application/json' \
      -d '{"username":"admin","password":"admin123"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access"])')
curl -s $B/api/dashboard/summary/ -H "Authorization: Bearer $TOK"
curl -s -X POST $B/api/telemetry -H 'X-Auth: fuelguardx' -H 'X-Device-Id: esp32-01' \
     -d '{"device_id":"esp32-01","latitude":21.14,"longitude":81.66,"speed_kmph":72,"satellites":9,"recording":true,"lock_active":false}'
```
