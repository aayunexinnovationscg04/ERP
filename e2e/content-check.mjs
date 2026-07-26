// Content-check: log into each app, visit every route, assert the main content
// region actually rendered something (catches blank-render regressions that the
// console-error check misses, e.g. multi-root component under <transition>).
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = process.env.BASE || 'https://erp.aayunexinnovations.com';
let CREDS = {};
try { CREDS = JSON.parse(fs.readFileSync(new URL('./creds.json', import.meta.url))); } catch {}

const APPS = {
  dealer: { ...CREDS.dealer, routes: ['/', '/fleet', '/alerts', '/geofences'] },
  admin:  { ...CREDS.admin,  routes: ['/users', '/roles', '/platform'] },
  pilot:  { ...CREDS.pilot,  routes: ['/', '/trips', '/alerts'] },
};
const MIN = 15; // chars of visible text expected in .main
let bad = 0;

const run = async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  for (const [app, cfg] of Object.entries(APPS)) {
    const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, ignoreHTTPSErrors: true });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push(e.message));
    await page.goto(`${BASE}/${app}/`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.locator('form input').nth(0).fill(cfg.user);
    await page.locator('input[type=password]').fill(cfg.pass);
    await page.locator('button.primary').first().click();
    await page.waitForSelector('.main', { state: 'visible', timeout: 20000 });
    for (const route of cfg.routes) {
      await page.goto(`${BASE}/${app}/#${route}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(1800);
      const len = (await page.locator('.main').innerText().catch(() => '')).trim().length;
      const ok = len >= MIN;
      if (!ok) bad++;
      console.log(`${ok ? '✓' : '✗ BLANK'}  ${app}${route}  (main text: ${len} chars)`);
    }
    await ctx.close();
  }
  await browser.close();
  console.log(`\n${bad === 0 ? 'ALL PAGES RENDER CONTENT ✓' : bad + ' BLANK PAGE(S) ✗'}`);
  process.exit(bad ? 1 : 0);
};
run().catch((e) => { console.error(e); process.exit(2); });
