import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import DiscoverHomeView from './DiscoverHomeView.vue'
const props = {
  connected: false,
  stats: { lit_cities: 0, memories: 0, photos: 0, vlog_minutes: 0 },
}
function button(wrapper: ReturnType<typeof mount>, text: string) {
  const result = wrapper.findAll('button').find((b) => b.text().trim() === text)
  if (!result) throw Error(text)
  return result
}
describe('发现首页：真实可操作的灵感入口', () => {
  it('显示三座目的地和素材署名，未连接不声称个人旅行记录', () => {
    const wrapper = mount(DiscoverHomeView, { props })
    expect(wrapper.findAll('.destination-card')).toHaveLength(3)
    expect(wrapper.find('a[href="/discover/credits.html"]').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('已经点亮')
  })
  it('海边主题只保留匹配目的地，切回全部恢复', async () => {
    const wrapper = mount(DiscoverHomeView, { props })
    await button(wrapper, '海边放空').trigger('click')
    expect(wrapper.findAll('.destination-card')).toHaveLength(1)
    expect(wrapper.find('.destination-card').attributes('aria-label')).toBe('规划厦门旅行')
    await button(wrapper, '全部灵感').trigger('click')
    expect(wrapper.findAll('.destination-card')).toHaveLength(3)
  })
  it('目的地卡片发送可编辑的城市和旅行想法', async () => {
    const wrapper = mount(DiscoverHomeView, { props })
    await wrapper.find('[aria-label="规划杭州旅行"]').trigger('click')
    expect(wrapper.emitted('plan')?.[0]?.[0]).toMatchObject({
      cityAdcode: '330100',
      goal: expect.stringContaining('杭州'),
      pace: 'relaxed',
    })
  })
  it('明确城市的搜索保留原始想法，不替换成固定攻略', async () => {
    const wrapper = mount(DiscoverHomeView, { props })
    const goal = '厦门三天，想去公园，下午休息'
    await wrapper.find('input[type=search]').setValue(goal)
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('plan')?.[0]?.[0]).toMatchObject({ cityAdcode: '350200', goal })
    await wrapper.find('[aria-label="清空搜索"]').trigger('click')
    expect(wrapper.find<HTMLInputElement>('input[type=search]').element.value).toBe('')
    await button(wrapper, '西湖边走走').trigger('click')
    expect(wrapper.emitted('plan')?.[1]?.[0]).toMatchObject({
      cityAdcode: '330100',
      goal: '杭州西湖散步',
    })
  })
  it('主题或歧义城市需要主动选择，不暗中猜目的地', async () => {
    const wrapper = mount(DiscoverHomeView, { props })
    await wrapper.find('input[type=search]').setValue('喜欢自然风景，想放松一点')
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('plan')).toBeUndefined()
    expect(wrapper.find('[aria-label="选择旅行目的地"]').exists()).toBe(true)
    await wrapper
      .findAll('.search-city-options button')
      .find((b) => b.text().includes('成都'))!
      .trigger('click')
    expect(wrapper.emitted('plan')?.[0]?.[0]).toMatchObject({
      cityAdcode: '510100',
      goal: expect.stringContaining('喜欢自然风景'),
    })
  })
})
