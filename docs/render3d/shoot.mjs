import { chromium } from 'playwright';
const shots = JSON.parse(process.argv[2]);
const browser = await chromium.launch({ ...(process.env.CHROME ? { executablePath: process.env.CHROME } : {}), args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 2000, height: 1250 } });
page.on('console', m => console.log('console:', m.text()));
page.on('pageerror', e => console.log('pageerror:', e.message));
for (const [name, hash] of Object.entries(shots)) {
  const w = +(new URLSearchParams(hash).get('w') || 2000), h = +(new URLSearchParams(hash).get('h') || 1250);
  await page.setViewportSize({ width: w, height: h });
  await page.goto(`http://127.0.0.1:8765/scene.html#${hash}`);
  await page.reload();
  await page.waitForFunction('window.__done === true', null, { timeout: 300000 });
  await page.locator('canvas').screenshot({ path: `${name}.png` });
  console.log('shot', name);
}
await browser.close();
