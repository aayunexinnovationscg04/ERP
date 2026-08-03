# Deployment / hosting

How the ERP is served on the pilot VPS (31.42.125.144). These files are the
source-of-truth copies of what's installed on the box. See also
`PORTS_AND_LINKS.txt` at the repo root for the full port map and live URLs.

## Architecture (current)
One public hostname, **erp.aayunexinnovations.com**, TLS terminated by
**Caddy** on 443, reverse-proxied to **nginx** on `127.0.0.1:8090` (loopback
only — no public plaintext port). nginx path-routes:

| Path | Serves |
|------|--------|
| `/dealer/` | Dealer ERP SPA (Vite base=`/dealer/`) |
| `/admin/`  | Admin ERP SPA (Vite base=`/admin/`) |
| `/pilot/`  | Pilot ERP SPA (Vite base=`/pilot/`) |
| `/api/`    | Django REST API (gunicorn `127.0.0.1:8000`) |
| `/django-admin/` | Django admin — NOT publicly routed, SSH-tunnel only |
| `/` | Landing page ("pick your portal") from `/var/www/fuelguardx/landing/` |

Legacy device telemetry (`/api/telemetry`, plain HTTP, port 80) is still
served by Caddy → the old receiver on `:8080`, unchanged by any of the above.

## Components
- **`fuelguardx.service`** → `/etc/systemd/system/fuelguardx.service`
  Runs Django under gunicorn (3 workers) on `127.0.0.1:8000`. Enabled at boot.
- **`nginx-fuelguardx.conf`** → the one nginx server block for everything above.
- Built SPA assets + landing page live under `/var/www/fuelguardx/{dealer,admin,pilot,landing}/`.

## Why assets live in /var/www (not /root)
nginx workers run as `www-data`, which cannot traverse `/root` (mode 700).
So collected static and the built SPAs are placed under `/var/www/fuelguardx/`,
which www-data can read. `STATIC_ROOT` in Django settings points there.

## Common commands
```bash
# Django service (after backend code/settings/migration changes)
cd /root/erp/backend && .venv/bin/python manage.py migrate
systemctl restart fuelguardx
systemctl status fuelguardx
journalctl -u fuelguardx -f         # live logs

# nginx (only needed if nginx-fuelguardx.conf itself changes)
nginx -t && systemctl reload nginx
tail -f /var/log/nginx/fuelguardx.error.log

# collect static after backend/admin changes
cd /root/erp/backend && .venv/bin/python manage.py collectstatic --noinput

# deploy the Dealer SPA
cd /root/erp/dealer-erp && npm run build
rm -rf /var/www/fuelguardx/dealer && cp -r dist /var/www/fuelguardx/dealer

# deploy the Pilot SPA
cd /root/erp/pilot-erp && npm run build
rm -rf /var/www/fuelguardx/pilot && cp -r dist /var/www/fuelguardx/pilot

# deploy the Admin SPA
cd /root/erp/admin-erp && npm run build
rm -rf /var/www/fuelguardx/admin && cp -r dist /var/www/fuelguardx/admin

# deploy the landing page
cp -r /root/erp/landing/* /var/www/fuelguardx/landing/
```

Prefer a swap-not-clobber deploy for a live rollback path, e.g.:
```bash
mv /var/www/fuelguardx/dealer /var/www/fuelguardx/dealer.bak
cp -r /root/erp/dealer-erp/dist /var/www/fuelguardx/dealer
# if something's wrong: mv /var/www/fuelguardx/dealer.bak /var/www/fuelguardx/dealer (after removing the bad one)
```

## Not yet done
- **Device cutover** — `/api/telemetry` still served by Caddy → old receiver on
  `:8080`. Repoint to Django's own ingest endpoint once ready, with a real
  per-device token (see PHASE1_SPEC.md).
