/** Read-only capture of the real, authenticated planner. Never creates tasks or writes profile data. */
import { chromium } from '@playwright/test'
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
const base = process.env.VOYAURA_PREVIEW_URL ?? 'http://127.0.0.1:5188/'
const token = readFileSync(new URL('../../.local/access-token.txt', import.meta.url), 'utf8').trim()
const folder = new URL('../../docs/design/round2/screenshots/', import.meta.url)
mkdirSync(folder, { recursive: true })
const browser = await chromium.launch({ channel: 'chrome', headless: true })
const results = []
try {
  for (const [name, width, height] of [
    ['desktop', 1440, 1000],
    ['tablet', 768, 1024],
    ['mobile', 390, 844],
    ['narrow', 320, 812],
  ]) {
    const context = await browser.newContext({
      viewport: { width, height },
      isMobile: width < 600,
      hasTouch: width < 600,
    })
    const page = await context.newPage()
    const errors = [],
      mutations = []
    page.on('pageerror', (e) => errors.push(e.message))
    page.on('request', (r) => {
      if (
        new URL(r.url()).pathname.startsWith('/api/') &&
        !['GET', 'HEAD', 'OPTIONS'].includes(r.method())
      )
        mutations.push({ method: r.method(), path: new URL(r.url()).pathname })
    })
    await page.goto(base)
    await page.getByRole('button', { name: '规划杭州旅行', exact: true }).click()
    await page.getByLabel('访问令牌', { exact: true }).fill(token)
    await page.getByRole('button', { name: '连接 Voyaura', exact: true }).click()
    await page.getByLabel('这次想怎样旅行？', { exact: true }).waitFor()
    await page.getByLabel('出发日期', { exact: true }).fill('2026-12-01')
    await page.getByLabel('出发日期', { exact: true }).blur()
    await page.evaluate(() => document.fonts.ready)
    await page.locator('.workspace-scroll').evaluate((el) => {
      el.scrollTop = 0
    })
    await page.screenshot({
      path: fileURLToPath(new URL(`brief-${name}.png`, folder)),
      animations: 'disabled',
    })
    await page.locator('.preferences-card').scrollIntoViewIfNeeded()
    await page.screenshot({
      path: fileURLToPath(new URL(`preferences-${name}.png`, folder)),
      animations: 'disabled',
    })
    results.push({
      name,
      width,
      height,
      errors,
      mutations,
      layout: await page.evaluate(() => ({
        viewport: innerWidth,
        documentWidth: document.documentElement.scrollWidth,
        scrollWidth: document.querySelector('.workspace-scroll').scrollWidth,
        scrollClientWidth: document.querySelector('.workspace-scroll').clientWidth,
      })),
      images: await page
        .locator('.agent-workspace img')
        .evaluateAll((images) =>
          images.map((i) => ({
            src: i.getAttribute('src'),
            loaded: i.complete && i.naturalWidth > 0,
          })),
        ),
    })
    await context.close()
  }
} finally {
  await browser.close()
}
writeFileSync(
  new URL('../../docs/design/round2/input-viewport-check.json', import.meta.url),
  JSON.stringify(results, null, 2),
)
console.log(JSON.stringify(results, null, 2))
if (
  results.some(
    (r) =>
      r.errors.length ||
      r.mutations.length ||
      r.layout.scrollWidth > r.layout.scrollClientWidth ||
      r.images.some((i) => !i.loaded),
  )
)
  throw new Error('Planner viewport validation failed; inspect input-viewport-check.json')
