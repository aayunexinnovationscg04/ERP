# Deployment / hosting

How the ERP is served on the pilot VPS (31.42.125.144). These files are the
source-of-truth copies of what's installed on the box.

## Port map
| Port | Service | Scope | Purpose |
|------|---------|-------|---------|
| 80 / 443 | **Caddy** | public | legacy device endpoint (`/api/telemetry` → old receiver on :8080). Unchanged. |
| 8090 | **nginx** | public | Fuel Guard X ERP front door (this setup) |
| 8000 | **gunicorn** | local | Django API + admin (`fuelguardx.service`) |
| 5432 | PostgreSQL | local | database |

nginx runs on **8090** deliberately so it does not collide with Caddy on 80/443.

## Components
- **`fuelguardx.service`** → `/etc/systemd/system/fuelguardx.service`
  Runs Django under gunicorn (3 workers) on `127.0.0.1:8000`. Enabled at boot.
- **`nginx-fuelguardx.conf`** → `/etc/nginx/sites-available/fuelguardx`
  (symlinked into `sites-enabled/`). Reverse-proxies `/api/` and `/admin/` to
  gunicorn, serves `/django-static/` from `/var/www/fuelguardx/static/`, and
  serves the Owner SPA from `/var/www/fuelguardx/owner/`.

## Why assets live in /var/www (not /root)
nginx workers run as `www-data`, which cannot traverse `/root` (mode 700).
So collected static and the built SPA are placed under `/var/www/fuelguardx/`,
which www-data can read. `STATIC_ROOT` in Django settings points there.

## Common commands
```bash
# Django service
systemctl restart fuelguardx        # after code/settings changes
systemctl status fuelguardx
journalctl -u fuelguardx -f         # live logs

# nginx
nginx -t && systemctl reload nginx
tail -f /var/log/nginx/fuelguardx.error.log

# collect static after frontend/admin changes
cd /root/erp/backend && .venv/bin/python manage.py collectstatic --noinput

# deploy the Owner SPA (once built)
cd /root/erp/owner-erp && npm run build
rm -rf /var/www/fuelguardx/owner && cp -r dist /var/www/fuelguardx/owner
```

## Not yet done
- **TLS on 8090** — currently plain HTTP. Add a cert (certbot) or, when we retire
  Caddy, move the ERP to 443. See the commented 443 block approach in the spec.
- **Device cutover** — `/api/telemetry` still served by Caddy → old receiver on
  :8080. Repoint to Django once the ingest endpoint is built.
