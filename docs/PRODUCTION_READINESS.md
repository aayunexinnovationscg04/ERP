# Fuel Guard X — Production Readiness

_Last updated: 2026-07-26_

This is the go-live reference for the pilot (5–30 trucks). It states honestly what
is production-ready, what is verified, and what is **blocked** (and on what).

## 1. What is live

One HTTPS host, path-routed, TLS by Caddy → nginx (loopback) → gunicorn → PostgreSQL.

| Portal | URL | Who |
|---|---|---|
| Dealer / Owner ERP | https://erp.aayunexinnovations.com/dealer/ | company owners/managers |
| Super Admin ERP | https://erp.aayunexinnovations.com/admin/ | platform staff |
| Driver ERP | https://erp.aayunexinnovations.com/pilot/ | drivers (mobile) |
| Backend API | https://erp.aayunexinnovations.com/api/ | shared |
| Django admin | https://erp.aayunexinnovations.com/django-admin/ | platform staff |

## 2. Verification (how each layer is tested)

- **Backend unit + API tests:** `cd backend && .venv/bin/python manage.py test` — auth,
  RBAC (owner/driver blocked from admin), company scoping, driver isolation, geofence
  CRUD, platform health, plus the derivation engine (haversine, geofence, overspeed,
  trip, tamper, offline).
- **Deploy check:** `.venv/bin/python manage.py check --deploy` — clean except the 3
  intentional HSTS/SSL-redirect warnings (Caddy owns the redirect; HSTS is set at Caddy).
- **Headless browser E2E:** `node e2e/run.mjs` — logs into all three apps, visits every
  page, screenshots desktop + mobile, and fails on any console/page error.

## 3. Security posture (done)

- `DEBUG=False`; secrets only in gitignored `backend/.env` (mode 600).
- JWT auth, 2h access token; login throttled 10/min per IP.
- nginx bound to `127.0.0.1` — no plaintext public port; only Caddy/TLS is public.
- Security headers + HSTS; `server_tokens off`; unused public `/api/telemetry` blocked.
- systemd sandboxing on the gunicorn unit; `ufw` allows only 22/80/443.
- PostgreSQL bound to `127.0.0.1`.
- Default passwords rotated → `deploy/PILOT_CREDENTIALS.txt` (gitignored).

## 4. Pre-go-live checklist

- [ ] Change all pilot passwords again and distribute over a secure channel.
- [ ] Set up **PostgreSQL backups** (nightly `pg_dump` + offsite copy). NOT yet configured.
- [ ] Confirm Let's Encrypt auto-renew (Caddy handles it; verify after ~60 days).
- [ ] Decide device cutover plan: when moving the device from the legacy Caddy receiver
      to the Django ingest, issue a **strong per-device INGEST token** (current token
      `fuelguardx` is firmware-baked and weak) and re-enable `/api/telemetry` in nginx.
- [ ] Add uptime monitoring / alerting on `/api/health` and `/api/admin/health`.
- [ ] Optional: relocate the project out of `/root` (e.g. `/opt/fuelguardx`) so gunicorn
      can drop from root to an unprivileged user.

## 5. Blocked / out-of-scope (needs hardware or paid APIs)

These are built-to-spec but cannot be truthfully "completed" in software alone:

- **All fuel analytics** (current level, refill/theft detection, consumption, efficiency,
  trends, low-fuel/theft alerts) — **BLOCKED: the flow sensor reports 0 in every real
  record.** Logic is coded and stays inert until the hardware vendor confirms the sensor
  is wired and reporting non-zero. Verify on a real truck, then these light up with no
  code change.
- **Turn-by-turn navigation, ETA, route planning/optimization, delivery timelines** —
  need a paid maps routing API (Google/Mapbox) + key. Not wired.
- **AI analytics** (mileage/fuel/maintenance/delay prediction) — Phase 3; needs a data
  history + model. Not built.
- **ERP/billing** (orders, challans, invoices, expenses) — Phase 3 business module.
- **Driver attendance / performance / salary** — Phase 2 HR module.

## 6. Operations quick reference

```
# services
systemctl status fuelguardx            # gunicorn (Django API)
systemctl status nginx caddy postgresql
systemctl status fuelguardx-offline.timer   # marks devices offline every 2 min

# logs
journalctl -u fuelguardx -f
tail -f /var/log/nginx/fuelguardx.error.log

# redeploy a frontend (example: driver)
cd /root/erp/driver-erp && npm run build && \
  rm -rf /var/www/fuelguardx/pilot && cp -r dist /var/www/fuelguardx/pilot && \
  chmod -R a+rX /var/www/fuelguardx/pilot

# backend after code change
systemctl restart fuelguardx
```
