import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import AccountHomeView from './AccountHomeView.vue'
import type { AgentRun } from '../api/agent'
import type { MapOverview } from '../types'
enableAutoUnmount(afterEach)
const { getAgentCapabilities, getImageStyles, listAgentRuns } = vi.hoisted(
  () => ({
    getAgentCapabilities: vi.fn(),
    getImageStyles: vi.fn(),
    listAgentRuns: vi.fn(),
  }),
)
vi.mock('../api/agent', () => ({ getAgentCapabilities, listAgentRuns }))
vi.mock('../api/client', () => ({ getImageStyles }))
const overview: MapOverview = {
  username: 'explicit-unit-owner',
  map_center: [104, 35],
  default_zoom: 4,
  stats: { lit_cities: 2, memories: 3, photos: 4, vlog_minutes: 0 },
  visited_cities: [],
  year_summaries: [],
}
const task: AgentRun = {
  id: 'explicit-unit-task',
  title: '明确标注的测试任务',
  kind: 'plan',
  status: 'needs_input',
  revision: 1,
  request: {},
  result: { intent_source: 'local_rules', verification_status: 'information_missing', summary: '明确标注的测试结果', warnings: [], unknowns: [] },
  events: [],
  created_at: '2026-11-23T01:00:00Z',
  updated_at: '2026-11-23T01:00:00Z',
  saved_artifact_id: null,
}
beforeEach(() => {
  vi.resetAllMocks()
  getAgentCapabilities.mockResolvedValue({
    amap_configured: false,
    model_configured: false,
    tools: [],
    limits: {},
  })
  getImageStyles.mockResolvedValue({ available: false })
  listAgentRuns.mockResolvedValue({ items: [task] })
})
describe('档案总览（明确组件测试输入）', () => {
  it('访客只看引导，不读取私人API或把空统计显示为已读取的档案', async () => {
    const wrapper = mount(AccountHomeView, {
      props: { overview, connected: false, hasSession: false },
    })
    await flushPromises()
    expect(wrapper.find('.account-identity').exists()).toBe(false)
    expect(getAgentCapabilities).not.toHaveBeenCalled()
    expect(getImageStyles).not.toHaveBeenCalled()
    expect(listAgentRuns).not.toHaveBeenCalled()
    await wrapper.get('.account-connect-state button').trigger('click')
    expect(wrapper.emitted('connect')).toEqual([[]])
  })
  it('展示实际统计、未配置状态和最近任务，打开只发事件', async () => {
    const wrapper = mount(AccountHomeView, {
      props: { overview, connected: true, hasSession: true },
    })
    await flushPromises()
    expect(
      wrapper.findAll('.account-identity dd').map((el) => el.text()),
    ).toEqual(['2', '3', '4'])
    expect(wrapper.text()).toContain('尚未连接')
    expect(wrapper.get('.account-task-status').text()).toBe('待补充')
    await wrapper.get('.account-task-list button').trigger('click')
    expect(wrapper.emitted('openRun')?.[0]).toEqual([task])
    expect(listAgentRuns).toHaveBeenCalledTimes(1)
  })
  it('服务状态读取失败不阻塞历史，也不假称已连接', async () => {
    getAgentCapabilities.mockRejectedValue(
      new Error('explicit local status error'),
    )
    getImageStyles.mockRejectedValue(
      new Error('explicit local image status error'),
    )
    const wrapper = mount(AccountHomeView, {
      props: { overview, connected: true, hasSession: true },
    })
    await flushPromises()
    expect(wrapper.get('.account-task-list').text()).toContain(task.title)
    expect(wrapper.findAll('.account-capabilities .ready')).toHaveLength(0)
    expect(wrapper.text()).toContain('暂无法确认')
  })
  it('任务读取失败允许主动重试，不伪造空历史', async () => {
    listAgentRuns.mockRejectedValueOnce(new Error('明确的测试读取失败'))
    const wrapper = mount(AccountHomeView, {
      props: { overview, connected: true, hasSession: true },
    })
    await flushPromises()
    expect(wrapper.find('.account-no-tasks').exists()).toBe(false)
    expect(wrapper.get('[role=alert]').text()).toContain('明确的测试读取失败')
    await wrapper.get('[role=alert] button').trigger('click')
    await flushPromises()
    expect(wrapper.get('.account-task-list').text()).toContain(task.title)
  })
  it('连接状态改变后忽略尚未返回的私人读取结果', async () => {
    let finish!: (value: { items: AgentRun[] }) => void
    listAgentRuns.mockReturnValue(
      new Promise((resolve) => {
        finish = resolve
      }),
    )
    const wrapper = mount(AccountHomeView, {
      props: { overview, connected: true, hasSession: true },
    })
    await wrapper.setProps({ connected: false, hasSession: false })
    finish({ items: [task] })
    await flushPromises()
    expect(wrapper.find('.account-task-list').exists()).toBe(false)
    expect(wrapper.find('.account-identity').exists()).toBe(false)
  })
})
