import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory } from 'vue-router'
import { createProductRouter } from './router'
import App from './App.vue'
const fetchMock = vi.fn()
vi.stubGlobal('fetch', fetchMock)
beforeEach(() => {
  sessionStorage.clear()
  fetchMock.mockReset()
  fetchMock.mockRejectedValue(new Error('explicit offline test'))
})
async function setup(path = '/') {
  const router = createProductRouter(createMemoryHistory())
  await router.push(path)
  await router.isReady()
  const wrapper = mount(App, { global: { plugins: [router] } })
  await flushPromises()
  return { wrapper, router }
}
describe('Voyaura发现入口与按需身份连接', () => {
  it('首次打开可浏览发现，不弹连接框也不读取私人API', async () => {
    const { wrapper } = await setup()
    expect(wrapper.find('[aria-label="旅行发现首页"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('下一段旅程')
    expect(wrapper.find('[role=dialog]').exists()).toBe(false)
    expect(fetchMock).not.toHaveBeenCalled()
  })
  it('点击目的地后才请求连接，关闭后仍可继续浏览', async () => {
    const { wrapper, router } = await setup()
    await wrapper.find('[aria-label="规划厦门旅行"]').trigger('click')
    await flushPromises()
    expect(wrapper.find('[role=dialog]').exists()).toBe(true)
    expect(router.currentRoute.value.path).toBe('/')
    expect(fetchMock).not.toHaveBeenCalled()
    await wrapper.find('[aria-label="关闭连接窗口"]').trigger('click')
    expect(wrapper.find('[role=dialog]').exists()).toBe(false)
    expect(wrapper.find('[aria-label="旅行发现首页"]').exists()).toBe(true)
  })
  it('直接进入私人计划路由时先连接，发现首页保留可见', async () => {
    const { wrapper, router } = await setup('/plan')
    expect(router.currentRoute.value.path).toBe('/')
    expect(wrapper.find('[role=dialog]').exists()).toBe(true)
    expect(wrapper.find('[aria-label="旅行发现首页"]').exists()).toBe(true)
  })
})
