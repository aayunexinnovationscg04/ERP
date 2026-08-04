// Verify admin-erp mobile UX against the local dev server (not prod).
import { chromium } from 'playwright';
import fs from 'fs';

const BASE = 'http://127.0.0.1:5175/admin/';
const SHOTS = '/tmp/claude-0/-root/f5d22171-f394-46dc-86a0-d1cf4d84238b/scratchpad/shots';
fs.mkdirSync(SHOTS, { recursive: true });
const CREDS = JSON.parse(fs.readFileSync('/root/erp/e2e/creds.json'));

const WIDTHS = [
  { w: 360, h: 780, label: '360' },
  { w: 390, h: 844, label: '390' },
  { w: 430, h: 932, label: '430' },
  { w: 768, h: 1024, label: '768-tablet' },
];

const ROUTES = [
  ['users', '/users'],
  ['roles', '/roles'],
  ['platform', '/platform'],
  ['company-analytics', '/company-analytics'],
  ['fleet-monitoring', '/fleet-monitoring'],
  ['devices', '/devices'],
  ['security-analytics', '/security-analytics'],
  ['reports', '/reports'],
  ['companies', '/companies'],
  ['platform-logs', '/platform-logs'],
];

async function run() {
  const b = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const results = [];

  for (const vp of WIDTHS) {
    const ctx = await b.newContext({ viewport: { width: vp.w, height: vp.h } });
    const p = await ctx.newPage();
    await p.goto(BASE, { waitUntil: 'networkidle' });
    await p.screenshot({ path: `${SHOTS}/login-${vp.label}.png` });

    // login
    await p.locator('form input').nth(0).fill(CREDS.admin.user);
    await p.locator('input[type=password]').fill(CREDS.admin.pass);
    await p.locator('button.primary').first().click();
    await p.waitForSelector('.main', { state: 'visible', timeout: 20000 });
    await p.waitForTimeout(400);

    for (const [label, route] of ROUTES) {
      await p.goto(`${BASE}#${route}`, { waitUntil: 'networkidle' }).catch(() => {});
      await p.waitForTimeout(500);
      const m = await p.evaluate(() => ({
        scrollW: document.documentElement.scrollWidth,
        innerW: window.innerWidth,
      }));
      const overflow = m.scrollW - m.innerW;
      results.push({ vp: vp.label, label, overflow });
      if (vp.w <= 430) {
        await p.screenshot({ path: `${SHOTS}/${label}-${vp.label}.png`, fullPage: true });
      } else if (label === 'roles' || label === 'users') {
        await p.screenshot({ path: `${SHOTS}/${label}-${vp.label}.png`, fullPage: true });
      }
    }

    // open the full-screen mobile menu on phone widths only, screenshot open + closed states
    if (vp.w <= 430) {
      await p.goto(`${BASE}#/users`, { waitUntil: 'networkidle' });
      await p.waitForTimeout(300);
      const burger = p.locator('.hamburger');
      await burger.first().click();
      await p.waitForTimeout(400);
      await p.screenshot({ path: `${SHOTS}/menu-open-${vp.label}.png` });
      // check it's truly full screen + opaque
      const sidebarBox = await p.locator('.sidebar').boundingBox();
      const sidebarBg = await p.locator('.sidebar').evaluate((el) => getComputedStyle(el).backgroundColor);
      results.push({ vp: vp.label, label: 'menu-sidebar-box', overflow: JSON.stringify(sidebarBox) });
      results.push({ vp: vp.label, label: 'menu-sidebar-bg', overflow: sidebarBg });
      // close via X
      const closeBtn = p.locator('.mobile-close-btn');
      const closeBox = await closeBtn.boundingBox();
      results.push({ vp: vp.label, label: 'close-btn-box', overflow: JSON.stringify(closeBox) });
      await closeBtn.click();
      await p.waitForTimeout(400);
      await p.screenshot({ path: `${SHOTS}/menu-closed-${vp.label}.png` });
      const stillOpen = await p.locator('.sidebar.open').count();
      results.push({ vp: vp.label, label: 'still-open-after-close', overflow: stillOpen });

      // reopen, click a nav group + a link, confirm it navigates and closes
      await burger.first().click();
      await p.waitForTimeout(400);
      const rolesLink = p.locator('a[href*="#/roles"]');
      if (await rolesLink.count()) {
        // accordion group for roles might need opening
        await rolesLink.first().click({ trial: false }).catch(() => {});
        await p.waitForTimeout(400);
      }
      const stillOpenAfterNav = await p.locator('.sidebar.open').count();
      results.push({ vp: vp.label, label: 'still-open-after-nav-click', overflow: stillOpenAfterNav });
      await p.screenshot({ path: `${SHOTS}/menu-after-nav-click-${vp.label}.png` });
    }

    await ctx.close();
  }
  await b.close();

  console.log(JSON.stringify(results, null, 2));
  const bad = results.filter(r => typeof r.overflow === 'number' && r.overflow > 2);
  console.log(bad.length ? `\n${bad.length} OVERFLOW(S)` : '\nNO HORIZONTAL OVERFLOW');
}
run().catch(e => { console.error(e); process.exit(1); });
