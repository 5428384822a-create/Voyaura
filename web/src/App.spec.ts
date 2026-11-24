import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App.vue'

vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('API offline')))

beforeEach(() => {
  vi.mocked(fetch).mockReset()
  vi.mocked(fetch).mockRejectedValue(new Error('API offline'))
})

describe('Voyaura shell', () => {
  it('opens on the map and exposes Xiaoxi', () => {
    const wrapper = mount(App)
    expect(wrapper.text()).toContain('你好，Aurora')
    expect(wrapper.text()).toContain('小曦')
    expect(wrapper.find('[aria-label="中国旅行地图"]').exists()).toBe(true)
  })

  it('submits a planning preview to Xiaoxi and renders unverified candidates', async () => {
    vi.mocked(fetch).mockImplementation(async (input) => {
      const url = String(input)
      if (!url.includes('/xiaoxi/planning/preview')) throw new Error('API offline')
      return new Response(JSON.stringify({
        status: 'ready_for_poi_search',
        assistant_message: '我先整理杭州三天的摄影候选。',
        requirements: {
          city_name: '杭州市', day_count: 3, party_type: 'solo', pace: 'relaxed',
          interests: ['摄影'], must_visit_names: [], avoid_names: [],
          dietary_constraints: [], transport_modes: ['transit'],
          daily_start_time: null, daily_end_time: null, total_budget_yuan: null,
        },
        city_adcode: null,
        missing_fields: [],
        clarification_questions: [],
        candidate_target_count: 30,
        recommended_daily_attractions: { min: 2, max: 3 },
        attraction_hypotheses: [{
          name: '西湖风景名胜区', category: 'photography',
          reason: '摄影主题候选，具体信息待核验。', priority: 5,
        }],
        search_themes: [{
          keyword: '杭州 摄影景点', category: 'photography',
          reason: '扩展摄影地点。', desired_count: 10,
        }],
        assumptions: [],
        warnings: ['模型建议仅用于候选检索，不代表地点已存在或适合最终行程。'],
        provider: 'deepseek',
        model: 'deepseek-chat',
        generated_at: '2026-11-13T10:00:00Z',
      }), { status: 200, headers: { 'Content-Type': 'application/json' } })
    })
    const wrapper = mount(App)
    await wrapper.get('[aria-label="打开小曦"]').trigger('click')
    await wrapper.get('[aria-label="给小曦发消息"]').setValue('杭州三天，独自摄影，轻松一些')
    await wrapper.get('.chat-composer').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('我先整理杭州三天的摄影候选')
    expect(wrapper.text()).toContain('候选池 30 个')
    expect(wrapper.text()).toContain('西湖风景名胜区')
    expect(wrapper.text()).toContain('模型建议仅用于候选检索')
  })

  it('closes Xiaoxi when navigating to the journey workspace', async () => {
    const wrapper = mount(App)

    await wrapper.get('[aria-label="打开小曦"]').trigger('click')
    expect(wrapper.find('[aria-label="小曦旅行助手"]').exists()).toBe(true)

    await wrapper.findAll('button[title="行程"]')[0]!.trigger('click')
    await flushPromises()

    expect(wrapper.find('[aria-label="小曦旅行助手"]').exists()).toBe(false)
    expect(wrapper.text()).toContain('行程计划')
    expect(wrapper.text()).toContain('智能规划')
  })
})
