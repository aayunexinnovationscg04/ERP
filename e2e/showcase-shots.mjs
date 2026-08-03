// Captures desktop + mobile screenshots of every current page in both ERPs,
// against the local dev servers (freshest code, including uncommitted work).
import { chromium } from 'playwright';
import fs from 'fs';

const SHOTS = process.cwd() + '/shots-showcase';
fs.mkdirSync(SHOTS, { recursive: true });

const DESKTOP = { width: 1440, height: 900 };
const MOBILE = { width: 390, height: 844 };

const APPS = {
  dealer: {
    base: 'http://localhost:5173',
    user: 'dealer', pass: 'dealer123',
    routes: [
      ['locations', '/locations'],
      ['vehicles', '/vehicles'],
      ['vehicle-detail', '/vehicles/7'],
      ['fuel', '/fuel'],
      ['fuel-detail', '/fuel/7'],
      ['pilots', '/pilots'],
      ['pilot-detail', '/pilots/5'],
      ['alerts', '/alerts'],
      ['geofences', '/geofences'],
    ],
  },
  pilot: {
    base: 'http://localhost:5174',
    user: 'pilot', pass: 'pilot123',
    routes: [
      ['home', '/'],
      ['trips', '/trips'],
      ['alerts', '/alerts'],
    ],
  },
};

async function login(page, base, user, pass) {
  await page.goto(`${base}/`, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForSelector('input', { timeout: 15000 });
  await page.locator('form input').nth(0).fill(user);
  await page.locator('input[type=password]').fill(pass);
  await page.locator('button.primary').first().click();
  await page.waitForSelector('.main', { state: 'visible', timeout: 20000 });
  await page.waitForTimeout(1200);
}

const run = async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });

  for (const [app, cfg] of Object.entries(APPS)) {
    // login screen, both sizes
    for (const [vp, name] of [[DESKTOP, 'desktop'], [MOBILE, 'mobile']]) {
      const ctx = await browser.newContext({ viewport: vp });
      const page = await ctx.newPage();
      await page.goto(`${cfg.base}/`, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(800);
      await page.screenshot({ path: `${SHOTS}/${app}-login-${name}.png` });
      await ctx.close();
    }

    // desktop authed pages
    {
      const ctx = await browser.newContext({ viewport: DESKTOP });
      const page = await ctx.newPage();
      await login(page, cfg.base, cfg.user, cfg.pass);
      for (const [label, route] of cfg.routes) {
        await page.goto(`${cfg.base}/#${route}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
        await page.waitForTimeout(1800);
        await page.screenshot({ path: `${SHOTS}/${app}-${label}-desktop.png` });
      }
      await ctx.close();
    }

    // mobile authed pages
    {
      const ctx = await browser.newContext({ viewport: MOBILE });
      const page = await ctx.newPage();
      await login(page, cfg.base, cfg.user, cfg.pass);
      for (const [label, route] of cfg.routes) {
        await page.goto(`${cfg.base}/#${route}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
        await page.waitForTimeout(1800);
        await page.screenshot({ path: `${SHOTS}/${app}-${label}-mobile.png` });
      }
      // drawer open shot from first route
      await page.goto(`${cfg.base}/#${cfg.routes[0][1]}`, { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(1000);
      const burger = page.locator('.hamburger');
      if (await burger.count()) {
        await burger.first().click();
        await page.waitForTimeout(500);
        await page.screenshot({ path: `${SHOTS}/${app}-drawer-mobile.png` });
      }
      await ctx.close();
    }
  }

  await browser.close();
  console.log('done ->', SHOTS);
};
run().catch((e) => { console.error(e); process.exit(1); });
