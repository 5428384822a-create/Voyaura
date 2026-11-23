import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import AMapLoader from '@amap/amap-jsapi-loader'
import AgentRouteMap from './AgentRouteMap.vue'
import type { AgentDay } from '../api/agent'
vi.mock('@amap/amap-jsapi-loader', () => ({ default: { load: vi.fn() } }))
const days: AgentDay[] = [1, 2].map((day) => ({
  day,
  date: `2026-12-0${day}`,
  start: '09:00',
  end: '11:00',
  total_minutes: 120,
  legs: [],
  stops: [0, 1].map((i) => ({
    candidate_id: `${day}-${i}`,
    name: `[地图夹具] ${day}.${i + 1}`,
    longitude: 113.3 + day * 0.01 + i * 0.01,
    latitude: 23.1 + day * 0.01 + i * 0.01,
    arrival: '09:00',
    departure: '10:00',
    stay_minutes: 60,
    timing_basis: 'user_schedule',
    source: 'user_provided',
  })),
}))
const props = { days, activeDay: 1, allowExternal: false }
function sdkFixture() {
  const maps: MapFixture[] = [],
    markers: MarkerFixture[] = [],
    paths: PathFixture[] = []
  class MapFixture {
    add = vi.fn()
    destroy = vi.fn()
    setFitView = vi.fn()
    constructor(..._args: unknown[]) {
      maps.push(this)
    }
  }
  class MarkerFixture {
    content: HTMLButtonElement
    constructor(options: { content: HTMLButtonElement }) {
      this.content = options.content
      markers.push(this)
    }
  }
  class PathFixture {
    setOptions = vi.fn()
    constructor(..._args: unknown[]) {
      paths.push(this)
    }
  }
  return {
    maps,
    markers,
    paths,
    sdk: { Map: MapFixture, Marker: MarkerFixture, Polyline: PathFixture },
  }
}
beforeEach(() => {
  vi.resetAllMocks()
  vi.stubEnv('VITE_AMAP_KEY', '')
  vi.stubEnv('VITE_AMAP_SECURITY_CODE', '')
})
afterEach(() => vi.unstubAllEnvs())
describe('地点地图交互与SDK适配边界（明确本地替身，非在线高德验收）', () => {
  it('缺少授权或Key时不加载地图SDK，使用明确标注的坐标示意', async () => {
    vi.stubEnv('VITE_AMAP_KEY', 'explicit-test-key')
    const wrapper = mount(AgentRouteMap, { props })
    await flushPromises()
    expect(AMapLoader.load).not.toHaveBeenCalled()
    vi.stubEnv('VITE_AMAP_KEY', '')
    await wrapper.setProps({ allowExternal: true })
    await flushPromises()
    expect(AMapLoader.load).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('非导航底图')
    wrapper.unmount()
  })
  it('坐标编号支持键盘选择，选中状态跟随实际日期与站点', async () => {
    const wrapper = mount(AgentRouteMap, { props })
    const point = wrapper.find('[aria-label="地图地点：第2天第1站 [地图夹具] 2.1"]')
    await point.trigger('keydown', { key: 'Enter' })
    expect(wrapper.emitted('select')?.[0]).toEqual([{ day: 2, candidateId: '2-0' }])
    await wrapper.setProps({ activeDay: 2, selectedStopId: '2-0' })
    expect(point.attributes('aria-pressed')).toBe('true')
    expect(wrapper.findAll('.map-marker.selected')).toHaveLength(1)
    wrapper.unmount()
  })
  it('SDK加载失败时如实降级，坐标编号仍可选择', async () => {
    vi.stubEnv('VITE_AMAP_KEY', 'explicit-test-key')
    vi.mocked(AMapLoader.load).mockRejectedValue(new Error('explicit local SDK failure fixture'))
    const wrapper = mount(AgentRouteMap, { props: { ...props, allowExternal: true } })
    await flushPromises()
    expect(wrapper.text()).toContain('底图暂时不可用')
    await wrapper.find('.map-marker').trigger('click')
    expect(wrapper.emitted('select')?.[0]).toEqual([{ day: 1, candidateId: '1-0' }])
    wrapper.unmount()
  })
  it('SDK替身验证日切换与高亮只更新现有实例，布局变更先清理旧实例', async () => {
    vi.stubEnv('VITE_AMAP_KEY', 'explicit-test-key')
    const fake = sdkFixture()
    vi.mocked(AMapLoader.load).mockResolvedValue(fake.sdk)
    const wrapper = mount(AgentRouteMap, { props: { ...props, allowExternal: true } })
    await flushPromises()
    expect(fake.maps).toHaveLength(1)
    await wrapper.setProps({ activeDay: 2, selectedStopId: '2-0' })
    expect(AMapLoader.load).toHaveBeenCalledTimes(1)
    expect(fake.maps).toHaveLength(1)
    expect(fake.markers[2]!.content.getAttribute('aria-pressed')).toBe('true')
    expect(fake.maps[0]!.setFitView).toHaveBeenLastCalledWith(
      [fake.markers[2], fake.markers[3]],
      true,
      [35, 35, 35, 35],
      16,
    )
    fake.markers[3]!.content.click()
    expect(wrapper.emitted('select')?.[0]).toEqual([{ day: 2, candidateId: '2-1' }])
    await wrapper.setProps({ compact: true })
    await flushPromises()
    expect(fake.maps[0]!.destroy).toHaveBeenCalledTimes(1)
    expect(fake.maps).toHaveLength(2)
    wrapper.unmount()
    expect(fake.maps[1]!.destroy).toHaveBeenCalledTimes(1)
  })
  it('卸载后到达的SDK响应不再创建地图', async () => {
    vi.stubEnv('VITE_AMAP_KEY', 'explicit-test-key')
    const fake = sdkFixture()
    let finish: (value: typeof fake.sdk) => void = () => {}
    vi.mocked(AMapLoader.load).mockImplementationOnce(
      () =>
        new Promise((resolve) => {
          finish = resolve
        }),
    )
    const wrapper = mount(AgentRouteMap, { props: { ...props, allowExternal: true } })
    await flushPromises()
    wrapper.unmount()
    finish(fake.sdk)
    await flushPromises()
    expect(fake.maps).toHaveLength(0)
  })
})
