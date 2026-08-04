// Pilot ERP mobile review screenshots — local dev server, real backend on :8000.
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = process.env.BASE || 'http://127.0.0.1:5174/pilot/';
const SHOTS = process.env.SHOTS || (process.cwd() + '/shots');
fs.mkdirSync(SHOTS, { recursive: true });

const CREDS = JSON.parse(fs.readFileSync('/root/erp/e2e/creds.json'));
const { user, pass } = CREDS.pilot;

const WIDTHS = [
  { width: 375, height: 812, tag: '375' },
  { width: 430, height: 932, tag: '430' },
];
const DESKTOP = { width: 1440, height: 900 };
const ROUTES = [['home', '/'], ['trips', '/trips'], ['alerts', '/alerts']];

async function login(page) {
  await page.goto(BASE, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForSelector('input', { timeout: 15000 });
  await page.locator('form input').nth(0).fill(user);
  await page.locator('input[type=password]').fill(pass);
  await page.locator('button.primary').first().click();
  await page.waitForSelector('.main', { state: 'visible', timeout: 20000 });
  await page.waitForTimeout(1200);
}

const run = async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });

  // login page at each mobile width
  for (const vp of WIDTHS) {
    const ctx = await browser.newContext({ viewport: vp, ignoreHTTPSErrors: true });
    const page = await ctx.newPage();
    await page.goto(BASE, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(600);
    await page.screenshot({ path: `${SHOTS}/login-${vp.tag}.png`, fullPage: true });
    await ctx.close();
    console.log(`login-${vp.tag} done`);
  }

  // authed pages at each mobile width
  for (const vp of WIDTHS) {
    const ctx = await browser.newContext({ viewport: vp, ignoreHTTPSErrors: true });
    const page = await ctx.newPage();
    await login(page);
    for (const [label, route] of ROUTES) {
      await page.goto(BASE + '#' + route, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(1600);
      await page.screenshot({ path: `${SHOTS}/${label}-${vp.tag}.png`, fullPage: true });
      const m = await page.evaluate(() => ({ scrollW: document.documentElement.scrollWidth, innerW: window.innerWidth }));
      const overflow = m.scrollW - m.innerW;
      console.log(`${label}-${vp.tag}: overflow=${overflow}`);
    }
    await ctx.close();
  }

  // desktop sanity check + breakpoint transition (760/761px)
  {
    const ctx = await browser.newContext({ viewport: DESKTOP, ignoreHTTPSErrors: true });
    const page = await ctx.newPage();
    await login(page);
    await page.screenshot({ path: `${SHOTS}/desktop-home.png`, fullPage: false });
    // collapse sidebar and shoot again
    await page.locator('.collapse-btn').first().click();
    await page.waitForTimeout(400);
    await page.screenshot({ path: `${SHOTS}/desktop-home-collapsed.png`, fullPage: false });
    console.log('desktop shots done');
    await ctx.close();
  }

  // breakpoint transition widths
  for (const w of [700, 760, 761, 800]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: 900 }, ignoreHTTPSErrors: true });
    const page = await ctx.newPage();
    await login(page);
    await page.screenshot({ path: `${SHOTS}/breakpoint-${w}.png`, fullPage: false });
    await ctx.close();
    console.log(`breakpoint-${w} done`);
  }

  await browser.close();
};
run().catch((e) => { console.error(e); process.exit(2); });
