import { chromium } from 'playwright';
import fs from 'fs';

const BASE = 'http://127.0.0.1:5175/admin/';
const SHOTS = '/tmp/claude-0/-root/f5d22171-f394-46dc-86a0-d1cf4d84238b/scratchpad/shots';
const CREDS = JSON.parse(fs.readFileSync('/root/erp/e2e/creds.json'));

async function run() {
  const b = await chromium.launch({ headless: true, args: ['--no-sandbox'] });

  // 1) full desktop width sanity check
  {
    const ctx = await b.newContext({ viewport: { width: 1280, height: 900 } });
    const p = await ctx.newPage();
    await p.goto(BASE, { waitUntil: 'networkidle' });
    await p.locator('form input').nth(0).fill(CREDS.admin.user);
    await p.locator('input[type=password]').fill(CREDS.admin.pass);
    await p.locator('button.primary').first().click();
    await p.waitForSelector('.main', { state: 'visible' });
    await p.waitForTimeout(400);
    await p.goto(`${BASE}#/roles`, { waitUntil: 'networkidle' });
    await p.waitForTimeout(400);
    await p.screenshot({ path: `${SHOTS}/desktop-1280-roles.png`, fullPage: true });
    const cardOverflow = await p.locator('.card').first().evaluate(el => getComputedStyle(el).overflowX);
    console.log('desktop 1280 .card overflow-x (should be visible, not auto):', cardOverflow);

    // test collapse button
    const collapseBtn = p.locator('.collapse-btn');
    console.log('collapse-btn visible at 1280:', await collapseBtn.isVisible());
    const collapseBox = await collapseBtn.boundingBox();
    console.log('collapse-btn box:', JSON.stringify(collapseBox));
    await collapseBtn.click();
    await p.waitForTimeout(300);
    await p.screenshot({ path: `${SHOTS}/desktop-1280-collapsed.png` });
    await collapseBtn.click();
    await p.waitForTimeout(300);

    // theme toggle position check - should be just above logout button
    const themeBox = await p.locator('.sidebar .theme-toggle').boundingBox();
    const logoutBox = await p.locator('.logout-btn').boundingBox();
    console.log('theme-toggle box:', JSON.stringify(themeBox));
    console.log('logout-btn box:', JSON.stringify(logoutBox));
    console.log('theme-toggle directly above logout (gap < 30px):', logoutBox.y - (themeBox.y + themeBox.height));

    // sidebar full height check
    const sidebarBox = await p.locator('.sidebar').boundingBox();
    console.log('sidebar box (should be full viewport height 900):', JSON.stringify(sidebarBox));

    await ctx.close();
  }

  // 2) tablet 768: verify table ACTUALLY scrolls horizontally (not just visual cue)
  {
    const ctx = await b.newContext({ viewport: { width: 768, height: 1024 } });
    const p = await ctx.newPage();
    await p.goto(BASE, { waitUntil: 'networkidle' });
    await p.locator('form input').nth(0).fill(CREDS.admin.user);
    await p.locator('input[type=password]').fill(CREDS.admin.pass);
    await p.locator('button.primary').first().click();
    await p.waitForSelector('.main', { state: 'visible' });
    await p.goto(`${BASE}#/roles`, { waitUntil: 'networkidle' });
    await p.waitForTimeout(400);
    const card = p.locator('.card').filter({ has: p.locator('table') }).first();
    const before = await card.evaluate(el => el.scrollLeft);
    await card.evaluate(el => { el.scrollLeft = 300; });
    const after = await card.evaluate(el => el.scrollLeft);
    console.log('tablet 768 roles table card scrollLeft before/after:', before, after);
    await p.screenshot({ path: `${SHOTS}/tablet-768-roles-scrolled.png` });
    await ctx.close();
  }

  await b.close();
}
run().catch(e => { console.error(e); process.exit(1); });
