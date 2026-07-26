# Fuel Guard X — Phase 1 Spec (Foundation + Owner ERP core)

## Context

**Why:** Aayunex is running a **pilot of 5–30 GPS/fuel-tracking trucks** (ESP32 + SIM800L on Airtel 2G).
The goal is to deliver the "Fuel Guard X" platform described in `documents/feature_list.pdf` and
`documents/Documentation.pdf` — three role-based ERPs (Owner, Driver, Super-Admin) over one shared
backend. The existing `receiver-dashboard` (a raw telemetry logger) is being **abandoned**; we build
fresh on **Django + PostgreSQL + Vue**.

**Hard reality from the real data** (82 records from device `esp32-01` in `receiver-dashboard/data/events.jsonl`):
- The device POSTs every ~60s to `POST /api/telemetry`, header `X-Auth: fuelguardx`, `X-Device-Id: esp32-01`.
- Payload fields: `device_id, latitude, longitude, speed_kmph, satellites, altitude_m, flow_rate_lpm,
  total_litres, recording, lock_active, gsm_signal`.
- **`flow_rate_lpm` and `total_litres` are `0` in every record** → fuel sensor unverified. GPS/speed/lock
  data is real and usable today.
- Only 1 device exists so far. Lat/long is sometimes `0,0` (no GPS fix) and must be filtered.

**Critical constraint:** the real ESP32 is already flashed pointing at `/api/telemetry` with token
`fuelguardx`. The new backend MUST expose that exact ingest contract or the live truck goes silent and
every device needs re-flashing. Phase 1 reimplements the ingest contract faithfully in Django.

**Phase 1 outcome:** a scalable multi-tenant backend + the Owner ERP live core (fleet grid, live map,
route history, telemetry panel, derived alerts), runnable on the one real device today. Driver ERP,
Super-Admin ERP, and billing/AI are Phases 2–3 on the same backend.

---

## Stack & decisions (confirmed with user)
- **Backend:** Django + Django REST Framework + Django Admin, PostgreSQL, JWT (SimpleJWT), RBAC.
- **Frontend:** three Vue 3 + Vite apps (one per ERP).
- **One shared backend + DB**; Vue apps are role-scoped views. No data duplication (multi-tenant by Company).
- Django Admin serves as the Super-Admin power tool in Phase 1 (dedicated Super-Admin Vue app in Phase 2).

## Repo layout
```
fuelguardx/
├── backend/                    # ONE Django project (config/)
│   ├── core/                   # Company, User (custom), roles, RBAC, JWT, CompanySettings
│   ├── fleet/                  # Vehicle, Device, Driver, Telemetry, Trip, Geofence, GeofenceEvent
│   ├── ingest/                 # /api/telemetry (firmware-compatible), Command queue
│   ├── alerts/                 # Alert model + derivation rules
│   ├── config/                 # settings, urls, asgi/wsgi
│   └── manage.py
├── owner-erp/                  # Vue app  (Phase 1)
├── driver-erp/                 # Vue app  (Phase 2, scaffold only in P1)
└── superadmin-erp/             # Vue app  (Phase 2)
```

---

## Data model (Postgres via Django models) — Phase 1

**Multi-tenancy:** `Company` is the tenant. Every business row FKs to Company. Every Owner API query is
filtered to `request.user.company`. Designed so 5 trucks or 30 trucks across 1..N companies is just data.

### core
- **Company**: `id, name, slug(unique), status(active|suspended), created_at`
- **User** (custom `AbstractUser`, set from line 1 — cannot change later): `+ company(FK,null for superadmin),
  role(OWNER|DRIVER|MANAGER|SUPERADMIN), phone`
- **CompanySettings** (1:1 Company): thresholds — `overspeed_limit_kmph(=60), offline_after_seconds(=900),
  low_fuel_litres(nullable), theft_drop_litres(=5), tamper_on_lock_change(bool)`

### fleet
- **Device**: `id, device_id(unique str e.g. "esp32-01"), company(FK), label, sim_number, firmware_version,
  last_seen, last_ip, online(derived bool), created_at`
- **Vehicle**: `id, company(FK), registration_number, make, model, tank_capacity_litres, device(OneToOne,null),
  active_driver(FK Driver,null), status(active|idle|offline|maintenance), created_at`
- **Driver** (minimal in P1; full mgmt P2): `id, company(FK), user(FK,null), name, phone, license_no`
- **Telemetry** (high-volume; the pilot's core table): `id, device(FK), vehicle(FK,null), device_ts,
  received_at, latitude, longitude, speed_kmph, satellites, altitude_m, flow_rate_lpm, total_litres,
  recording(bool), lock_active(bool), gsm_signal, has_gps_fix(bool derived), raw(JSONB — full payload)`
  Indexes: `(device, received_at)`, `(vehicle, received_at)`. Partition-ready but not partitioned at pilot scale.
- **Trip** (derived): `id, vehicle(FK), driver(FK,null), started_at, ended_at(null), start_lat/lng, end_lat/lng,
  distance_km, max_speed_kmph, avg_speed_kmph, fuel_consumed_litres, status(active|completed)`
- **Geofence**: `id, company(FK), name, kind(circle|polygon), center_lat/lng, radius_m, polygon(JSON,null),
  purpose(allowed|restricted|customer_site), active(bool)`
- **GeofenceEvent** (derived): `id, vehicle(FK), geofence(FK), event(enter|exit), ts, lat, lng`

### ingest
- **Command** (replaces `queues.json`): `id, device(FK), payload(open|testing), content_type, status(queued|
  delivered), created_at, delivered_at`. Allowed commands configurable per deployment.

### alerts
- **Alert**: `id, company(FK), vehicle(FK,null), device(FK,null), type, severity(info|warning|critical),
  title, message, lat, lng, meta(JSON), status(open|acknowledged|resolved), created_at, acknowledged_by(FK,null),
  acknowledged_at`. Indexes: `(company, status, created_at)`.
  Types: `OVERSPEED, GEOFENCE_BREACH, LOW_FUEL, FUEL_FILL, FUEL_THEFT, TAMPER, DEVICE_OFFLINE, SENSOR_FAULT`.

---

## Ingest contract — `POST /api/telemetry` (firmware-compatible, do not break)
Reimplements the proven `server.py` behavior on Postgres:
- **Auth:** token via header `X-Auth`/`X-Auth-Token`/`X-Token` OR query `?auth=|token=|key=`, compared with
  `hmac.compare_digest` against the ingest token (`fuelguardx` for the live device; per-company tokens supported).
- **Permissive:** accept any body; parse JSON when present, else store raw. Never reject on shape. 1 MB cap.
- **Identify device:** header `X-Device-Id` → body `device_id`/`deviceId`/… → query → fallback client IP.
  Auto-create `Device` on first sight; update `last_seen`, `last_ip`.
- **Store** one `Telemetry` row (typed columns + `raw` JSONB). Set `has_gps_fix = (satellites>0 and lat/lng!=0)`.
- **Run derivation** (below) synchronously for the pilot; extractable to Celery later.
- **Reply:** `{"ok": true, "device_id": ..., "received": <bytes>, "commands": [<queued Commands>]}` — draining
  the device's command queue in the same response (exactly-once, same as today).
- Rejected/unauthorized attempts recorded for the Super-Admin "blocked" view.

## Derivation engine (runs on each ingest; idempotent)
- **Trip:** `recording=true` starts/continues a trip; `recording=false` or a telemetry gap > `offline_after_seconds`
  closes it. Accumulate `distance_km` (haversine between consecutive **fixed** GPS points), `max/avg speed`,
  `fuel_consumed_litres` (Δ`total_litres`).
- **Overspeed:** `speed_kmph > overspeed_limit_kmph` → one `OVERSPEED` alert per continuous violation (debounced,
  not per-point).
- **Geofence:** point-in-circle/polygon test vs company's active geofences; on state change emit `GeofenceEvent`
  (+`GEOFENCE_BREACH` alert when entering a `restricted` zone or exiting an `allowed` zone).
- **Fuel fill:** Δ`total_litres` up beyond noise → `FUEL_FILL`. **Fuel theft:** fuel/level drop or flow while
  stationary → `FUEL_THEFT` (critical). **Low fuel:** derived level < `low_fuel_litres` → `LOW_FUEL`.
  *(All fuel rules coded to spec but INERT until the flow sensor reports non-zero — flagged, not blocking.)*
- **Tamper:** unexpected `lock_active` change / cap-open → `TAMPER`.
- **Device offline:** periodic sweep (management command run on interval/cron) marks `Device.online=false` and
  raises `DEVICE_OFFLINE` after `offline_after_seconds` (default 900s = the guide's 15-min "red" threshold).

---

## API (DRF, JWT-auth, all Owner routes scoped to `user.company`)
**Auth:** `POST /api/auth/login` (→access+refresh), `POST /api/auth/refresh`, `GET /api/auth/me`
**Dashboard:** `GET /api/dashboard/summary` (counts: total/active/idle/offline trucks, open alerts,
distance today, fuel today)
**Fleet:**
- `GET /api/vehicles/` (list + live status + latest telemetry snapshot)
- `GET /api/vehicles/{id}/`
- `GET /api/vehicles/{id}/telemetry/?from&to` (route history / playback)
- `GET /api/vehicles/{id}/trips/`, `GET /api/trips/{id}/`
- `GET /api/devices/`, `POST /api/devices/{id}/command` (queue `open`/`testing`)
**Geofences:** `GET/POST/PUT/DELETE /api/geofences/`
**Alerts:** `GET /api/alerts/?status&type&vehicle`, `POST /api/alerts/{id}/acknowledge`
**Ingest:** `POST /api/telemetry` (token auth, firmware-facing)
**Live updates:** Phase 1 uses **client polling** (`/dashboard/summary` + `/vehicles` every N s) — simplest and
ample for 30 trucks. WebSocket/SSE noted for later.
**Super-Admin:** Django Admin in Phase 1 (companies, users, devices, blocked list); DRF endpoints in Phase 2.

## RBAC
Role on `User`. DRF permission classes: `IsOwner` (company-scoped read/write), `IsDriver` (own vehicle/trips),
`IsSuperAdmin` (all). Every queryset filtered by company except Super-Admin. JWT carries role + company_id.

## Owner ERP screens (Vue 3 + Vite, `owner-erp/`)
1. **Login** (JWT).
2. **Dashboard** — KPI tiles (trucks total/active/idle/offline, open alerts, distance & fuel today), fleet map
   with all live truck markers, recent-alerts feed.
3. **Fleet list** — table/grid: status dot (green<3m / amber<15m / red), last seen, speed, fuel, GSM; row → detail.
4. **Vehicle detail** — live map marker, live telemetry panel, **route history/playback** (date range), trips
   list, per-vehicle alerts, "send command" button.
5. **Alerts** — filterable list, acknowledge action.
6. **Geofences** — draw on map (Leaflet) + list/manage.
Map: **Leaflet + OpenStreetMap tiles** (free, no key). Google/Mapbox deferred to Phase 3 (routing/ETA).
Master data (vehicles/drivers/assignment) via Django Admin in P1; dedicated screens in P2.

## Scalability (5 → 30+ trucks)
- Stateless JWT API → horizontally scalable. Postgres indexes on telemetry/alerts hot paths.
- Derivation is idempotent and O(1) per point; extractable to Celery+Redis when ingest volume grows.
- Telemetry table partition-ready (by month) — not needed at pilot scale, documented for later.
- Multi-tenant from line 1 so onboarding company #2..N is data, not code.

---

## Assumptions to confirm on review (defaults chosen; correct if wrong)
1. **Overspeed limit** default **60 km/h**; **offline** after **15 min** (matches guide). Adjustable per company.
2. **`lock_active` semantics:** assumed `true` = lock engaged/closed; a change to `false` on the move = tamper.
   (Confirm the sensor's polarity.)
3. **`total_litres` semantics:** assumed cumulative litres through a flow meter (monotonic). No tank-level sensor,
   so "current fuel level" = fills − consumption (drift acknowledged). Confirm with hardware vendor.
4. **Driver master data** is minimal in Phase 1 (name/assignment only); full driver mgmt + attendance/salary is P2.
5. Ingest token: keep global `fuelguardx` for the live device; per-company tokens supported but optional in pilot.

## Build milestones (Phase 1 execution order, once approved)
1. Scaffold repo; install Django/DRF/SimpleJWT/psycopg; Postgres DB + `config` project; custom User; settings.
2. `core` + `fleet` + `ingest` + `alerts` models + migrations + Django Admin registration.
3. `/api/telemetry` ingest endpoint (firmware-compatible) + Command queue; verify against live payload shape.
4. Derivation engine (trip/overspeed/geofence/tamper/offline; fuel rules inert) + offline sweep command.
5. Backfill script: import `receiver-dashboard/data/events.jsonl` → Telemetry (seed real data for the demo).
6. DRF API (auth, dashboard, vehicles, telemetry, trips, devices, geofences, alerts) + RBAC.
7. `owner-erp` Vue app: login, dashboard, fleet list, vehicle detail (live map + route history), alerts, geofences.
8. Scaffold `driver-erp` / `superadmin-erp` shells (Phase 2 placeholders).

## Verification (end-to-end)
- `python manage.py test` for models/derivation unit tests (trip close, overspeed debounce, geofence enter/exit,
  haversine distance).
- **Live ingest check** (mirrors the old guide): `curl -i -X POST http://localhost:8000/api/telemetry
  -H "X-Auth: fuelguardx" -H "X-Device-Id: esp32-01" -d '{"device_id":"esp32-01","latitude":21.1456,
  "longitude":81.6646,"speed_kmph":72,"satellites":9,"total_litres":0,"recording":true,"lock_active":false,
  "gsm_signal":14}'` → expect `200 {"ok":true,...}`, a Telemetry row, and an `OVERSPEED` alert (72>60).
- After backfill, open `owner-erp` → dashboard shows `esp32-01`, the route history renders the real GPS trail
  (with `0,0` points filtered), and idle/offline status matches `last_seen`.
- Point the real device (or `receiver-dashboard/fake_device.py` adapted) at the new endpoint → marker moves live.
