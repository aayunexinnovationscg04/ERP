// Headless E2E for Fuel Guard X — logs into each ERP, visits every page,
// captures screenshots (desktop + mobile) and records console/page errors.
// Usage: node run.mjs
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = process.env.BASE || 'https://erp.aayunexinnovations.com';
const SHOTS = process.env.SHOTS || (process.cwd() + '/shots');
fs.mkdirSync(SHOTS, { recursive: true });

// Credentials come from a gitignored creds.json (see creds.example.json) or env vars.
// NEVER hardcode passwords here — this file is committed.
let CREDS = {};
try { CREDS = JSON.parse(fs.readFileSync(new URL('./creds.json', import.meta.url))); } catch { /* fall back to env */ }
const cred = (app, envUser, envPass) => ({
  user: process.env[envUser] || CREDS[app]?.user,
  pass: process.env[envPass] || CREDS[app]?.pass,
});

const APPS = {
  dealer: {
    ...cred('dealer', 'DEALER_USER', 'DEALER_PASS'),
    routes: [['dashboard', '/'], ['fleet', '/fleet'], ['alerts', '/alerts'], ['geofences', '/geofences']],
  },
  admin: {
    ...cred('admin', 'ADMIN_USER', 'ADMIN_PASS'),
    routes: [['users', '/users'], ['roles', '/roles'], ['platform', '/platform']],
  },
  pilot: {
    ...cred('pilot', 'PILOT_USER', 'PILOT_PASS'),
    routes: [['mytruck', '/'], ['trips', '/trips'], ['alerts', '/alerts']],
  },
};

const DESKTOP = { width: 1280, height: 900 };
const MOBILE = { width: 390, height: 844 };
const report = [];

function watch(page, bucket) {
  page.on('console', (m) => { if (m.type() === 'error') bucket.push('console: ' + m.text()); });
  page.on('pageerror', (e) => bucket.push('pageerror: ' + e.message));
  page.on('requestfailed', (r) => {
    const u = r.url();
    if (u.includes('/api/') || u.includes('/assets/')) bucket.push('reqfail: ' + u + ' ' + (r.failure()?.errorText || ''));
  });
}

async function login(page, app, cfg) {
  await page.goto(`${BASE}/${app}/`, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForSelector('input', { timeout: 15000 });
  const inputs = page.locator('form input');
  await inputs.nth(0).fill(cfg.user);
  await page.locator('input[type=password]').fill(cfg.pass);
  await page.locator('button.primary, button[type=submit], form button').first().click();
  // .main is the post-login content region (visible on both desktop and mobile)
  await page.waitForSelector('.main', { state: 'visible', timeout: 20000 });
  await page.waitForTimeout(1200);
}

const run = async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  for (const [app, cfg] of Object.entries(APPS)) {
    // --- login page shots (desktop + mobile) ---
    for (const [vp, name] of [[DESKTOP, 'desktop'], [MOBILE, 'mobile']]) {
      const ctx = await browser.newContext({ viewport: vp, ignoreHTTPSErrors: true });
      const page = await ctx.newPage(); const errs = []; watch(page, errs);
      try {
        await page.goto(`${BASE}/${app}/`, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(800);
        await page.screenshot({ path: `${SHOTS}/${app}-login-${name}.png`, fullPage: false });
        report.push({ app, page: `login-${name}`, ok: true, errors: errs });
      } catch (e) {
        report.push({ app, page: `login-${name}`, ok: false, error: String(e), errors: errs });
      }
      await ctx.close();
    }

    // --- authed pages (desktop) ---
    {
      const ctx = await browser.newContext({ viewport: DESKTOP, ignoreHTTPSErrors: true });
      const page = await ctx.newPage(); const errs = []; watch(page, errs);
      try {
        await login(page, app, cfg);
        for (const [label, route] of cfg.routes) {
          const before = errs.length;
          await page.goto(`${BASE}/${app}/#${route}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
          await page.waitForTimeout(1600); // let data + map render
          await page.screenshot({ path: `${SHOTS}/${app}-${label}-desktop.png`, fullPage: false });
          report.push({ app, page: label, ok: true, newErrors: errs.slice(before) });
        }
      } catch (e) {
        report.push({ app, page: 'authed-flow', ok: false, error: String(e), errors: errs });
      }
      await ctx.close();
    }

    // --- one mobile authed shot (main page, shows hamburger) ---
    {
      const ctx = await browser.newContext({ viewport: MOBILE, ignoreHTTPSErrors: true });
      const page = await ctx.newPage(); const errs = []; watch(page, errs);
      try {
        await login(page, app, cfg);
        await page.goto(`${BASE}/${app}/#${cfg.routes[0][1]}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
        await page.waitForTimeout(1500);
        await page.screenshot({ path: `${SHOTS}/${app}-main-mobile.png`, fullPage: false });
        // open the hamburger drawer if present
        const burger = page.locator('.hamburger');
        if (await burger.count()) { await burger.first().click(); await page.waitForTimeout(500);
          await page.screenshot({ path: `${SHOTS}/${app}-drawer-mobile.png` }); }
        report.push({ app, page: 'mobile', ok: true, errors: errs });
      } catch (e) {
        report.push({ app, page: 'mobile', ok: false, error: String(e), errors: errs });
      }
      await ctx.close();
    }
  }
  await browser.close();

  console.log('\n===== E2E REPORT =====');
  let fails = 0, errcount = 0;
  for (const r of report) {
    const e = (r.errors || r.newErrors || []);
    if (!r.ok) fails++;
    errcount += e.length;
    const flag = r.ok ? (e.length ? '⚠ ' : '✓ ') : '✗ ';
    console.log(`${flag}${r.app}/${r.page}${r.ok ? '' : '  ERROR: ' + r.error}${e.length ? '  [' + e.length + ' err]' : ''}`);
    for (const x of e) console.log('      - ' + x.slice(0, 160));
  }
  console.log(`\nsummary: ${report.length} checks, ${fails} failed, ${errcount} console/page errors`);
  console.log('screenshots in: ' + SHOTS);
  fs.writeFileSync(`${SHOTS}/report.json`, JSON.stringify(report, null, 2));
  process.exit(fails ? 1 : 0);
};
run().catch((e) => { console.error(e); process.exit(2); });
