import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 45000,
  expect: { timeout: 10000 },
  reporter: [
    ['list'],
    ['junit', { outputFile: process.env.VOYAURA_E2E_REPORT ?? '../docs/design/round2-split/e2e.xml' }],
  ],
  outputDir: '../.local/playwright-artifacts',
  use: {
    baseURL: process.env.VOYAURA_E2E_WEB_URL ?? 'http://127.0.0.1:5188',
    channel: process.env.VOYAURA_E2E_CHANNEL ?? 'chrome',
    trace: 'off',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'desktop', use: { viewport: { width: 1440, height: 1000 } } },
    {
      name: 'mobile',
      use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true },
    },
  ],
})
