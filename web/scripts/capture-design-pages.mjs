import { chromium } from '../node_modules/playwright/index.mjs'
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
const mode = 'after'
// Reads only the local owner profile. Never log the token or write travel records.
const token = (process.env.VOYAURA_DESIGN_TOKEN ?? readFileSync(
  process.env.VOYAURA_DESIGN_TOKEN_FILE ?? new URL('../../.local/access-token.txt', import.meta.url), 'utf8',
)).trim()
const webURL = new URL(process.env.VOYAURA_DESIGN_WEB_URL ?? 'http://127.0.0.1:5188')
if (!['127.0.0.1','localhost'].includes(webURL.hostname)) throw new Error('本脚本仅截取本机服务；请配置本地 VOYAURA_DESIGN_WEB_URL。')
if (!token) throw new Error('请在本机环境变量或忽略的令牌文件中提供访问令牌。')
const output = new URL(`../../docs/design/governance/${mode}/`, import.meta.url)
mkdirSync(output, { recursive: true })
const browser = await chromium.launch({ channel: 'chrome', headless: true })
const errors = [], mutations = [], checks = []
try {
  for (const [name, width, height] of [['desktop',1440,1000], ['mobile',390,844], ...(mode === 'after' ? [['tablet',768,1024],['threshold',1280,1000],['narrow',320,812]] : [])]) {
    const context = await browser.newContext({ viewport: { width, height }, reducedMotion: 'reduce' })
    await context.addInitScript(value => sessionStorage.setItem('voyaura.access-token',value),token)
    const page = await context.newPage()
    await page.route('**/api/**', route => {
      if (!['GET','HEAD','OPTIONS'].includes(route.request().method())) return route.abort()
      return route.continue()
    })
    page.on('pageerror',e => errors.push(e.message))
    page.on('request',r => { if (new URL(r.url()).pathname.startsWith('/api/') && !['GET','HEAD','OPTIONS'].includes(r.method())) mutations.push(r.method()) })
    for (const [view,path] of [['discover','/'],['plan','/plan'],['atlas','/journey/map'],['memories','/journey/stories'],['story','/journey/stories?compose=story&city=440100'],['studio','/studio'],['account','/account']]) {
      await page.goto(new URL(path,webURL).href)
      await page.waitForLoadState('networkidle')
      await page.screenshot({path:fileURLToPath(new URL(`${view}-${name}.png`,output)), mask:[page.locator('.account-identity h2'),page.locator('.account-task-copy'),page.locator('.memory-card-city'),page.locator('.memory-card-date'),page.locator('.atlas-city-items strong')], maskColor:'#e4e4d4'})
      checks.push({view,name,...await page.evaluate(() => ({viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,scrollContainers:[...document.querySelectorAll('.discover-page,.journey-scroll,.studio-scroll,.workspace-scroll,.account-scroll')].map(el => ({width:el.clientWidth,scrollWidth:el.scrollWidth}))}))})
    }
    await context.close()
  }
} finally { await browser.close() }
writeFileSync(new URL('checks.json',output),JSON.stringify({checks,errors,mutations},null,2))
if (errors.length || mutations.length || checks.some(c => c.documentWidth > c.viewport || c.scrollContainers.some(s => s.scrollWidth>s.width))) throw new Error('Read-only viewport verification failed; inspect checks.json')
console.log(JSON.stringify({mode,views:checks.length,errors:errors.length,mutations:mutations.length}))
