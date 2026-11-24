import { chromium } from '@playwright/test'
import { mkdirSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
const folder = new URL('../../docs/design/round1/screenshots/', import.meta.url)
mkdirSync(folder, { recursive: true })
const browser = await chromium.launch({ channel: 'chrome', headless: true })
const results = []
const prefix = process.env.VOYAURA_CAPTURE_PREFIX ?? ''
for (const [name, width, height] of [
  ['desktop', 1440, 1000],
  ['tablet', 768, 1024],
  ['mobile', 390, 844],
  ['narrow', 320, 812],
]) {
  const context = await browser.newContext({
    viewport: { width, height },
    deviceScaleFactor: 1,
    isMobile: width < 600,
    hasTouch: width < 600,
  })
  const page = await context.newPage()
  const errors = []
  const apiCalls = []
  page.on('pageerror', (e) => errors.push(e.message))
  page.on('request', (r) => {
    if (new URL(r.url()).pathname.startsWith('/api/')) apiCalls.push(new URL(r.url()).pathname)
  })
  await page.goto(process.env.VOYAURA_PREVIEW_URL ?? 'http://127.0.0.1:5188/', {
    waitUntil: 'networkidle',
  })
  await page.getByRole('heading', { name: /下一段旅程/ }).waitFor()
  await page.locator('.hero-image').evaluate((img) => img.decode())
  await page.screenshot({
    path: fileURLToPath(new URL(`${prefix}discover-${name}.png`, folder)),
    animations: 'disabled',
  })
  await page.locator('.destination-section').scrollIntoViewIfNeeded()
  await page.screenshot({
    path: fileURLToPath(new URL(`${prefix}destinations-${name}.png`, folder)),
    animations: 'disabled',
  })
  results.push({
    name,
    width,
    height,
    errors,
    apiCalls,
    layout: await page.evaluate(() => ({
      viewport: innerWidth,
      documentWidth: document.documentElement.scrollWidth,
      mainWidth: document.querySelector('main')?.scrollWidth,
    })),
    images: await page
      .locator('img')
      .evaluateAll((images) =>
        images.map((i) => ({
          src: i.getAttribute('src'),
          loaded: i.complete && i.naturalWidth > 0,
        })),
      ),
  })
  await context.close()
}
await browser.close()
writeFileSync(
  new URL(`../../docs/design/round1/${prefix}viewport-check.json`, import.meta.url),
  JSON.stringify(results, null, 2),
)
console.log(JSON.stringify(results, null, 2))
