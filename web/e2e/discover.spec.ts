/** Real browser and API checks; homepage content is public editorial inspiration, not seeded user history. */
import { test, expect } from '@playwright/test'
import { readFileSync } from 'node:fs'
const token =
  process.env.VOYAURA_E2E_TOKEN ??
  readFileSync(new URL('../../.local/access-token.txt', import.meta.url), 'utf8').trim()
test('发现页无需令牌：主题筛选、城市澄清、照片与全局导航', async ({ page }) => {
  const apiCalls: string[] = []
  const errors: string[] = []
  page.on('request', (r) => {
    if (new URL(r.url()).pathname.startsWith('/api/')) apiCalls.push(new URL(r.url()).pathname)
  })
  page.on('pageerror', (e) => errors.push(e.message))
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /下一段旅程/ })).toBeVisible()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.locator('.destination-card')).toHaveCount(3)
  await page.getByRole('button', { name: '海边放空', exact: true }).click()
  await expect(page.locator('.destination-card')).toHaveCount(1)
  await page.getByRole('button', { name: '全部灵感', exact: true }).click()
  await expect(page.locator('.destination-card')).toHaveCount(3)
  await page.getByLabel('旅行搜索', { exact: true }).fill('想看看自然，放松一点')
  await page.getByRole('button', { name: '搜索并规划', exact: true }).click()
  await expect(page.getByRole('region', { name: '选择旅行目的地' })).toBeVisible()
  await expect(page.getByRole('dialog')).toHaveCount(0)
  expect(apiCalls).toEqual([])
  expect(errors).toEqual([])
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBeTruthy()
  for (const image of await page.locator('img').all())
    expect(
      await image.evaluate((el: HTMLImageElement) => el.complete && el.naturalWidth > 0),
    ).toBeTruthy()
})
test('目的地→按需连接→条件带入→刷新与返回，目标不写进URL', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: '规划杭州旅行', exact: true }).click()
  await expect(page.getByRole('dialog')).toBeVisible()
  await page.getByLabel('访问令牌', { exact: true }).fill(token)
  await page.getByRole('button', { name: '连接 Voyaura', exact: true }).click()
  await expect(page).toHaveURL(/\/plan$/)
  await expect(page.getByLabel('这次想怎样旅行？', { exact: true })).toHaveValue(/杭州/)
  await expect(page.getByLabel('目的地', { exact: true })).toHaveValue('330100')
  expect(page.url()).not.toContain('goal=')
  await page.reload()
  await expect(page.getByLabel('这次想怎样旅行？', { exact: true })).toHaveValue(/杭州/)
  await expect(page.getByLabel('目的地', { exact: true })).toHaveValue('330100')
  await page.goBack()
  await expect(page.getByRole('heading', { name: /下一段旅程/ })).toBeVisible()
  // Re-enter while connected: preserve a real history entry and the new destination.
  await page.getByRole('button', { name: '规划成都旅行', exact: true }).click()
  await expect(page).toHaveURL(/\/plan$/)
  await expect(page.getByRole('dialog')).toHaveCount(0)
  await expect(page.getByLabel('目的地', { exact: true })).toHaveValue('510100')
  await page.reload()
  await expect(page.getByLabel('这次想怎样旅行？', { exact: true })).toHaveValue(/成都/)
  await page.goBack()
  await expect(page.getByRole('heading', { name: /下一段旅程/ })).toBeVisible()
})
