# shared-db

The one PostgreSQL 16 database used by `shared-backend` (all three portals).

- Runs as a system service on `127.0.0.1:5432` (never exposed publicly), so the
  data itself lives in PostgreSQL's own directory, not here.
- Database `fuelguardx`, user `fuelguardx`; the password is in
  `shared-backend/.env` (`DATABASE_URL`, gitignored).
- Shell on the server: `su postgres -c "psql fuelguardx"`
- `backups/` (gitignored) holds dumps and config snapshots.

```bash
# back up
su postgres -c "pg_dump -Fc fuelguardx" > backups/fuelguardx-$(date +%Y%m%d-%H%M%S).dump
# restore (overwrites the database — be sure)
su postgres -c "pg_restore --clean --if-exists -d fuelguardx" < backups/<file>.dump
```
