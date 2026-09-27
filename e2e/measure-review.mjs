import { chromium } from 'playwright';
import fs from 'fs';
import { portalUrl } from './portals.mjs';
const CREDS = JSON.parse(fs.readFileSync('/root/aayunex_innovations/ERP/e2e/creds.json'));
const { user, pass } = CREDS.pilot;
const run = async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 }, ignoreHTTPSErrors: true });
  const page = await ctx.newPage();
  await page.goto(portalUrl('pilot'), { waitUntil: 'networkidle' });
  await page.locator('form input').nth(0).fill(user);
  await page.locator('input[type=password]').fill(pass);
  await page.locator('button.primary').first().click();
  await page.waitForSelector('.main', { state: 'visible', timeout: 20000 });
  await page.waitForTimeout(1500);
  const data = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.chip').forEach((chip, i) => {
      const body = chip.querySelector('.chip-body');
      const v = chip.querySelector('.v');
      const small = v.querySelector('small');
      out.push({
        i,
        chipRect: chip.getBoundingClientRect().width,
        bodyRect: body.getBoundingClientRect().width,
        vRect: v.getBoundingClientRect().width,
        vScrollWidth: v.scrollWidth,
        smallText: small?.textContent,
        vText: v.textContent.trim(),
        vFontSize: getComputedStyle(v).fontSize,
      });
    });
    return out;
  });
  console.log(JSON.stringify(data, null, 2));
  await ctx.close();
  await browser.close();
};
run();
