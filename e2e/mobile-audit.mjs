// Mobile responsiveness audit: every page at phone width. Flags horizontal
// overflow (document wider than viewport) and screenshots each for review.
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = process.env.BASE || 'https://erp.aayunexinnovations.com';
const SHOTS = process.env.SHOTS || (process.cwd() + '/mobile');
fs.mkdirSync(SHOTS, { recursive: true });
let CREDS = {};
try { CREDS = JSON.parse(fs.readFileSync(new URL('./creds.json', import.meta.url))); } catch {}

const W = 390, H = 844;
const APPS = {
  dealer: { ...CREDS.dealer, routes: [['dashboard','/'],['fleet','/fleet'],['alerts','/alerts'],['geofences','/geofences']] },
  admin:  { ...CREDS.admin,  routes: [['users','/users'],['roles','/roles'],['platform','/platform']] },
  pilot:  { ...CREDS.pilot,  routes: [['home','/'],['trips','/trips'],['alerts','/alerts']] },
};
const results = [];

async function measure(page, name, file) {
  await page.waitForTimeout(1600);
  const m = await page.evaluate(() => ({
    scrollW: document.documentElement.scrollWidth,
    innerW: window.innerWidth,
    bodyW: document.body.scrollWidth,
  }));
  const overflow = Math.max(m.scrollW, m.bodyW) - m.innerW;
  const bad = overflow > 2;
  results.push({ name, overflow, bad });
  await page.screenshot({ path: `${SHOTS}/${file}.png`, fullPage: true });
  console.log(`${bad ? '✗ OVERFLOW +' + overflow + 'px' : '✓ fits'}  ${name}`);
}

const run = async () => {
  const b = await chromium.launch({ headless: true, args: ['--no-sandbox'] });

  // landing (public)
  {
    const ctx = await b.newContext({ viewport: { width: W, height: H }, ignoreHTTPSErrors: true });
    const p = await ctx.newPage();
    await p.goto(`${BASE}/`, { waitUntil: 'networkidle', timeout: 30000 });
    await measure(p, 'landing', 'landing');
    await ctx.close();
  }

  for (const [app, cfg] of Object.entries(APPS)) {
    const ctx = await b.newContext({ viewport: { width: W, height: H }, ignoreHTTPSErrors: true });
    const p = await ctx.newPage();
    // login page
    await p.goto(`${BASE}/${app}/`, { waitUntil: 'networkidle', timeout: 30000 });
    await measure(p, `${app}/login`, `${app}-login`);
    // sign in
    await p.locator('form input').nth(0).fill(cfg.user);
    await p.locator('input[type=password]').fill(cfg.pass);
    await p.locator('button.primary').first().click();
    await p.waitForSelector('.main', { state: 'visible', timeout: 20000 });
    for (const [label, route] of cfg.routes) {
      await p.goto(`${BASE}/${app}/#${route}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
      await measure(p, `${app}/${label}`, `${app}-${label}`);
    }
    // open the hamburger drawer to check it too
    const burger = p.locator('.hamburger');
    if (await burger.count()) { await burger.first().click(); await p.waitForTimeout(500);
      await p.screenshot({ path: `${SHOTS}/${app}-drawer.png` }); }
    await ctx.close();
  }
  await b.close();

  const bad = results.filter(r => r.bad);
  console.log(`\n${bad.length ? bad.length + ' PAGE(S) OVERFLOW ✗' : 'ALL PAGES FIT THE VIEWPORT ✓'}`);
  console.log('screenshots: ' + SHOTS);
  process.exit(bad.length ? 1 : 0);
};
run().catch(e => { console.error(e); process.exit(2); });
