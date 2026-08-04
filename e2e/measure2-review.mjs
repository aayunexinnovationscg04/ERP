import { chromium } from 'playwright';
import fs from 'fs';
const CREDS = JSON.parse(fs.readFileSync('/root/erp/e2e/creds.json'));
const { user, pass } = CREDS.pilot;
const run = async () => {
  const browser = await chromium.launch({ headless: true, args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 }, ignoreHTTPSErrors: true });
  const page = await ctx.newPage();
  await page.goto('http://127.0.0.1:5174/pilot/', { waitUntil: 'networkidle' });
  await page.locator('form input').nth(0).fill(user);
  await page.locator('input[type=password]').fill(pass);
  await page.locator('button.primary').first().click();
  await page.waitForSelector('.main', { state: 'visible', timeout: 20000 });
  await page.waitForTimeout(1500);
  const data = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.chip').forEach((chip, i) => {
      const v = chip.querySelector('.v');
      v.style.whiteSpace = 'nowrap';
      out.push({ i, vText: v.textContent.trim(), unwrappedScrollWidth: v.scrollWidth, chipRect: chip.getBoundingClientRect().width, bodyWidth: chip.querySelector('.chip-body').getBoundingClientRect().width });
      v.style.whiteSpace = '';
    });
    // also grab column widths precisely
    const chips = [...document.querySelectorAll('.chip')].map(c => c.getBoundingClientRect());
    return { out, chipsRects: chips.map(r => ({x: r.x, w: r.width})) };
  });
  console.log(JSON.stringify(data, null, 2));
  await ctx.close();
  await browser.close();
};
run();
