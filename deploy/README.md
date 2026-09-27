# Deployment / hosting

How the ERP is served on the pilot VPS (31.42.125.144). The files in this folder
are the source-of-truth copies of what gets installed on the box. See also
`PORTS_AND_LINKS.txt` at the repo root for the port map and live URLs.

## Architecture
One subdomain per portal. **Caddy** terminates TLS on 443 for every hostname
(automatic Let's Encrypt certificates, auto-renewed — no certbot needed) and
reverse-proxies to **nginx** on `127.0.0.1:8090` (loopback only), which routes
by `Host`:

| Hostname | Serves |
|----------|--------|
| `erp.aayunexinnovations.com`    | Landing page "Choose your portal" (`/var/www/fuelguardx/landing/`) + permanent redirects for old `/dealer/…`, `/pilot/…`, `/admin/…`, `/django-admin/…` links |
| `dealer.aayunexinnovations.com` | Dealer ERP SPA (`/var/www/fuelguardx/dealer/`) + `/api/` |
| `pilot.aayunexinnovations.com`  | Pilot ERP SPA (`/var/www/fuelguardx/pilot/`) + `/api/` |
| `admin.aayunexinnovations.com`  | Admin ERP SPA (`/var/www/fuelguardx/admin/`) + `/api/` + `/django-admin/` |

Every SPA is built with Vite `base: '/'` and uses clean history-mode URLs
(`/users`, `/fleet-overview`, …). nginx falls back to `index.html` for any
client route. Old `#/…` links are rewritten to clean paths by the SPA itself.

Each portal is its own origin, so its session cookie and browser storage are
isolated from the others by the browser.

Legacy device telemetry (`/api/telemetry`, plain HTTP, port 80) is still
served by Caddy → the old receiver on `:8080`, unchanged by any of the above.

## Auth model (since the ui-revamp branch)
- Access token: 10 min JWT, held only in SPA memory, sent as `Authorization: Bearer`.
- Refresh token: `HttpOnly; Secure; SameSite=Strict` cookie `fgx_rt_<portal>`,
  path `/api/auth/`, rotated on every refresh, old one blacklisted.
- An account can only sign in to its own portal (admin → admin, dealer/manager
  → dealer, pilot → pilot). Changing a user's password, role, company or active
  flag signs them out everywhere immediately.
- Details: `backend/core/tokens.py`, `backend/core/authentication.py`, `docs/API.md`.

## Files
| Repo file | Installed as |
|-----------|--------------|
| `Caddyfile` | `/etc/caddy/Caddyfile` |
| `nginx-fuelguardx.conf` | `/etc/nginx/conf.d/fuelguardx.conf` |
| `nginx-snippets/*.conf` | `/etc/nginx/snippets/` |
| `fuelguardx.service` (+ sync/offline timers) | `/etc/systemd/system/` |

nginx workers run as `www-data`, which cannot traverse `/root` (mode 700), so
built SPAs, the landing page and Django's collected static live under
`/var/www/fuelguardx/`.

---

## One-time cutover: path-routed → subdomains (ui-revamp branch)

Do these in order. DNS for `erp`, `admin`, `dealer`, `pilot` already points at
31.42.125.144. Everyone has to sign in again once afterwards (old tokens don't
carry the new portal/session claims).

```bash
cd /root/aayunex_innovations/ERP

# 1. Backend settings — backend/.env
#    DJANGO_ALLOWED_HOSTS=admin.aayunexinnovations.com,dealer.aayunexinnovations.com,pilot.aayunexinnovations.com,localhost,127.0.0.1
#    CSRF_TRUSTED_ORIGINS=https://admin.aayunexinnovations.com
#    (CORS_ALLOWED_ORIGINS can stay as is; production is same-origin.)

# 2. Backend code: migrate (adds User.session_version + token blacklist tables), restart
cd backend
.venv/bin/python manage.py migrate
.venv/bin/python manage.py collectstatic --noinput
systemctl restart fuelguardx && systemctl status fuelguardx --no-pager
cd ..

# 3. Build and install the three SPAs (keep a .bak for rollback)
for app in dealer pilot admin; do
  (cd $app-erp && npm ci && npm run build) || break
  rm -rf /var/www/fuelguardx/$app.bak
  mv /var/www/fuelguardx/$app /var/www/fuelguardx/$app.bak
  cp -r $app-erp/dist /var/www/fuelguardx/$app
done

# 4. Landing page (replaces the old one; the old three.js/logo assets are gone)
rm -rf /var/www/fuelguardx/landing.bak && mv /var/www/fuelguardx/landing /var/www/fuelguardx/landing.bak
cp -r landing /var/www/fuelguardx/landing

# 5. nginx: host-routed config + snippets
cp /etc/nginx/conf.d/fuelguardx.conf /root/fuelguardx.conf.bak
mkdir -p /etc/nginx/snippets
cp deploy/nginx-snippets/*.conf /etc/nginx/snippets/
cp deploy/nginx-fuelguardx.conf /etc/nginx/conf.d/fuelguardx.conf
nginx -t && systemctl reload nginx

# 6. Caddy: add the new hostnames (certificates are issued automatically)
cp /etc/caddy/Caddyfile /root/Caddyfile.bak
cp deploy/Caddyfile /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile && systemctl reload caddy
journalctl -u caddy -n 50 --no-pager      # look for "certificate obtained successfully" x3

# 7. Verify
for h in erp admin dealer pilot; do curl -sI https://$h.aayunexinnovations.com/ | head -1; done
curl -s https://admin.aayunexinnovations.com/api/health                  # {"ok": true, ...}
curl -sI https://erp.aayunexinnovations.com/dealer/alerts | grep -i location   # -> https://dealer.../alerts
curl -s -X POST https://dealer.aayunexinnovations.com/api/auth/login \
     -H 'Content-Type: application/json' -H 'X-FGX-Portal: dealer' \
     -d '{"username":"dealer","password":"<password>"}' -i | grep -i "set-cookie"   # fgx_rt_dealer; HttpOnly; Secure; SameSite=Strict
```

### Rollback
```bash
cp /root/fuelguardx.conf.bak /etc/nginx/conf.d/fuelguardx.conf && nginx -t && systemctl reload nginx
cp /root/Caddyfile.bak /etc/caddy/Caddyfile && systemctl reload caddy
for app in dealer pilot admin landing; do rm -rf /var/www/fuelguardx/$app && mv /var/www/fuelguardx/$app.bak /var/www/fuelguardx/$app; done
# backend: check out the previous commit, then `systemctl restart fuelguardx`.
# The two new migrations are additive, so the old code runs fine against the migrated DB.
```

---

## Everyday commands
```bash
# Django (after backend code/settings/migration changes)
cd /root/aayunex_innovations/ERP/backend && .venv/bin/python manage.py migrate
systemctl restart fuelguardx
journalctl -u fuelguardx -f

# Backend tests (needs a Postgres role allowed to create the throwaway test DB)
DATABASE_URL=postgres://<role-with-CREATEDB>:<pw>@127.0.0.1:5432/postgres .venv/bin/python manage.py test

# Prune expired refresh-token records (rotation adds one per refresh). Run daily, e.g. cron:
#   17 3 * * * cd /root/aayunex_innovations/ERP/backend && .venv/bin/python manage.py flushexpiredtokens
.venv/bin/python manage.py flushexpiredtokens

# nginx (only if the conf or snippets change)
nginx -t && systemctl reload nginx
tail -f /var/log/nginx/fuelguardx.error.log

# Redeploy one SPA (swap, keep a rollback copy)
cd /root/aayunex_innovations/ERP/dealer-erp && npm run build
rm -rf /var/www/fuelguardx/dealer.bak && mv /var/www/fuelguardx/dealer /var/www/fuelguardx/dealer.bak
cp -r dist /var/www/fuelguardx/dealer

# Local development: run any portal against a local API
cd dealer-erp && API_TARGET=http://127.0.0.1:8000 npm run dev    # http://localhost:5173
```

## Not yet done
- **Device cutover** — `/api/telemetry` still served by Caddy → old receiver on
  `:8080`. Repoint to Django's own ingest endpoint once ready, with a real
  per-device token (see PHASE1_SPEC.md).
