# Fuel Guard X — ERP

AI-powered transport intelligence & fuel-security platform. One shared backend, three role-based ERPs.

## Monorepo layout

```
ERP/
├── backend/        # Django + DRF + Django Admin (PostgreSQL) — the shared brain
├── dealer-erp/     # Vue 3 + Vite → dealer.aayunexinnovations.com  (fleet owners / managers)
├── pilot-erp/      # Vue 3 + Vite → pilot.aayunexinnovations.com   (drivers, mobile-first)
├── admin-erp/      # Vue 3 + Vite → admin.aayunexinnovations.com   (platform admin)
├── landing/        # static page → erp.aayunexinnovations.com       ("choose your portal")
├── shared/
│   ├── design/     # tokens.css (one palette for all portals), brand mark
│   └── ui/         # shared Vue components (AuthShell sign-in screen + portal scenes)
├── deploy/         # Caddy, nginx (+ snippets), systemd units, deploy runbook
├── e2e/            # Playwright checks
└── docs/           # API + specs
```

One repo, but each app builds and deploys independently: Django as a JSON API, each Vue app as a
standalone SPA on its own subdomain (imports `@shared/...` at build time). The Vue apps are
**not** served by Django templates.

## Stack
- **Backend:** Django, Django REST Framework, Django Admin, PostgreSQL, JWT (SimpleJWT: short-lived access token in memory + rotating HttpOnly refresh cookie per portal), multi-tenant RBAC.
- **Frontend:** Vue 3 + Vite, Leaflet + OpenStreetMap for maps.

## Devices
ESP32 + SIM800L (Airtel 2G) POST telemetry to `POST /api/telemetry` with header `X-Auth: <token>`.
The ingest contract is firmware-compatible with the already-flashed pilot device (`esp32-01`).

## Status
Phase 1 in progress — foundation (multi-tenant models + ingest + derivation) and the Owner ERP live core.
See `docs/PHASE1_SPEC.md`.
