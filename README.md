# Fuel Guard X — ERP

AI-powered transport intelligence & fuel-security platform. One shared backend, three role-based ERPs.

## Monorepo layout

```
erp/
├── backend/            # Django + DRF + Django Admin  (PostgreSQL) — the shared brain
├── owner-erp/          # Vue 3 + Vite  → fleet owner / company view   (Phase 1)
├── driver-erp/         # Vue 3 + Vite  → driver operational view      (Phase 2)
├── superadmin-erp/     # Vue 3 + Vite  → platform-wide control        (Phase 2)
├── shared/             # shared Vue api-client + types the apps import
└── docs/               # specs & design docs
```

One repo, but each app builds and deploys independently: Django as a JSON API, each Vue app as a
standalone SPA. The Vue apps are **not** served by Django templates.

## Stack
- **Backend:** Django, Django REST Framework, Django Admin, PostgreSQL, JWT (SimpleJWT), multi-tenant RBAC.
- **Frontend:** Vue 3 + Vite, Leaflet + OpenStreetMap for maps.

## Devices
ESP32 + SIM800L (Airtel 2G) POST telemetry to `POST /api/telemetry` with header `X-Auth: <token>`.
The ingest contract is firmware-compatible with the already-flashed pilot device (`esp32-01`).

## Status
Phase 1 in progress — foundation (multi-tenant models + ingest + derivation) and the Owner ERP live core.
See `docs/PHASE1_SPEC.md`.
