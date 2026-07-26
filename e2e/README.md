# Fuel Guard X — headless E2E

Playwright script that logs into all three ERPs, visits every page (desktop + mobile),
screenshots each, and fails on any console/page error.

## Run
```
cd e2e
npm install            # first time
npx playwright install chromium
cp creds.example.json creds.json   # then fill in real pilot passwords (gitignored)
node run.mjs
```
Screenshots land in `e2e/shots/` (gitignored). Override with `SHOTS=/path` and `BASE=https://...`.
Credentials load from `creds.json` (gitignored) or env vars DEALER_PASS / ADMIN_PASS / PILOT_PASS.
