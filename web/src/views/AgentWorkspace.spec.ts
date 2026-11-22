import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import AgentWorkspace from './AgentWorkspace.vue'
import * as api from '../api/agent'
import type { AgentRun } from '../api/agent'

vi.mock('../api/agent', () => ({
  getAgentCapabilities: vi.fn(),
  listAgentRuns: vi.fn(),
  createAgentRun: vi.fn(),
  getAgentRun: vi.fn(),
  editAgentDraft: vi.fn(),
  previewAgentConfirmation: vi.fn(),
  confirmAgentRun: vi.fn(),
}))
const fixture = (): AgentRun => ({
  id: 'test-run',
  kind: 'plan',
  status: 'awaiting_confirmation',
  revision: 1,
  title: '明确的测试行程',
  request: { daily_end: '18:00', allow_external: false },
  created_at: '2026-11-22T00:00:00Z',
  updated_at: '2026-11-22T00:00:00Z',
  saved_artifact_id: null,
  result: {
    intent_source: 'local_rules',
    verification_status: 'conditional',
    summary: '本测试使用显式夹具，不代表在线地图。',
    warnings: [],
    unknowns: ['交通时间未核实'],
    candidates: [],
    days: [
      {
        day: 1,
        date: '2026-12-01',
        start: '09:00',
        end: '10:00',
        total_minutes: 60,
        legs: [],
        stops: [
          {
            candidate_id: 'c1',
            name: '夹具地点',
            longitude: 113.3,
            latitude: 23.1,
            arrival: '09:00',
            departure: '10:00',
            stay_minutes: 60,
            timing_basis: 'user_schedule',
            source: 'user_provided',
          },
        ],
      },
    ],
    validation: { checks: [], known_cost_yuan: 0, unknown_cost_count: 1 },
  },
  events: [],
})
function button(wrapper: ReturnType<typeof mount>, text: string) {
  const found = wrapper.findAll('button').find((b) => b.text().includes(text))
  if (!found) throw new Error(`找不到按钮 ${text}`)
  return found
}
beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(api.getAgentCapabilities).mockResolvedValue({
    amap_configured: false,
    model_configured: false,
    intent_default: 'local_rules',
    privacy_notice: '',
    limits: {},
    tools: [],
  })
  vi.mocked(api.listAgentRuns).mockResolvedValue({ items: [] })
  vi.mocked(api.createAgentRun).mockResolvedValue(fixture())
})
describe('小曦工作流交互边界（明确测试替身）', () => {
  it('默认不授权外部工具，条件草案须先预览再主动勾选才能保存', async () => {
    const wrapper = mount(AgentWorkspace)
    await flushPromises()
    await wrapper.find('textarea').setValue('测试两天的轻松行程')
    await wrapper.find('form.travel-brief').trigger('submit')
    await flushPromises()
    expect(api.createAgentRun).toHaveBeenCalledWith(
      expect.objectContaining({
        allow_external: false,
        allow_model: false,
        allow_memory_access: false,
        candidates: [],
      }),
    )
    expect(wrapper.text()).toContain('条件草案')
    expect(wrapper.text()).toContain('你提供的地点')
    expect(wrapper.text()).toContain('交通时间未核实')
    const proof = {
      confirmation_token: 'test-token',
      content_digest: 'test-digest',
      expires_at: '2099-01-01T00:00:00Z',
      revision: 1,
      summary: '测试预览',
      requires_unverified_acknowledgement: true,
    }
    vi.mocked(api.previewAgentConfirmation).mockResolvedValue(proof)
    await button(wrapper, '核对并保存当前草案').trigger('click')
    await flushPromises()
    expect(api.confirmAgentRun).not.toHaveBeenCalled()
    expect(button(wrapper, '确认保存到私人档案').attributes('disabled')).toBeDefined()
    await wrapper.find('.confirmation-card input[type=checkbox]').setValue(true)
    vi.mocked(api.confirmAgentRun).mockResolvedValue({
      ...fixture(),
      status: 'confirmed',
      saved_artifact_id: 'artifact-test',
    })
    await button(wrapper, '确认保存到私人档案').trigger('click')
    await flushPromises()
    expect(api.confirmAgentRun).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'test-run' }),
      proof,
      true,
    )
    expect(wrapper.text()).toContain('已妥善收藏')
  })
  it('网络失败保留同一请求号供重试，不重复创建新的操作', async () => {
    vi.mocked(api.createAgentRun)
      .mockRejectedValueOnce(new Error('测试网络中断'))
      .mockResolvedValueOnce(fixture())
    const wrapper = mount(AgentWorkspace)
    await flushPromises()
    await wrapper.find('textarea').setValue('测试请求重试')
    await wrapper.find('form.travel-brief').trigger('submit')
    await flushPromises()
    const first = vi.mocked(api.createAgentRun).mock.calls[0]![0]
    await button(wrapper, '重试同一任务').trigger('click')
    await flushPromises()
    expect(vi.mocked(api.createAgentRun).mock.calls[1]![0]).toEqual(first)
  })
  it('故事未授权不发请求，编辑后须保存新版本才允许预览确认', async () => {
    const story: AgentRun = {
      ...fixture(),
      kind: 'story',
      title: '测试故事',
      result: {
        ...fixture().result,
        verification_status: 'validated',
        days: [],
        story_body: '原始夹具记录。',
        source_memories: [],
      },
    }
    vi.mocked(api.createAgentRun).mockResolvedValue(story)
    const wrapper = mount(AgentWorkspace, { props: { initialKind: 'story' } })
    await flushPromises()
    await wrapper.find('textarea').setValue('整理测试回忆')
    await wrapper.find('form.travel-brief').trigger('submit')
    await flushPromises()
    expect(api.createAgentRun).not.toHaveBeenCalled()
    await wrapper.find('.travel-brief input[type=checkbox]').setValue(true)
    await wrapper.find('form.travel-brief').trigger('submit')
    await flushPromises()
    expect(api.createAgentRun).toHaveBeenCalledWith(
      expect.objectContaining({
        allow_memory_access: true,
        allow_external: false,
        allow_model: false,
      }),
    )
    await wrapper.find('.story-paper textarea').setValue('我编辑的测试故事。')
    expect(button(wrapper, '核对并保存当前草案').attributes('disabled')).toBeDefined()
    vi.mocked(api.editAgentDraft).mockResolvedValue({
      ...story,
      revision: 2,
      result: { ...story.result, story_body: '我编辑的测试故事。' },
    })
    await button(wrapper, '保存草稿修改').trigger('click')
    await flushPromises()
    expect(api.editAgentDraft).toHaveBeenCalledWith('test-run', {
      expected_revision: 1,
      title: '测试故事',
      story_body: '我编辑的测试故事。',
    })
    expect(button(wrapper, '核对并保存当前草案').attributes('disabled')).toBeUndefined()
  })
  it('空候选和服务未配置时显示信息不足，不提供确认保存', async () => {
    const missing = fixture()
    missing.status = 'needs_input'
    missing.result.verification_status = 'information_missing'
    missing.result.days = []
    vi.mocked(api.createAgentRun).mockResolvedValue(missing)
    const wrapper = mount(AgentWorkspace)
    await flushPromises()
    await wrapper.find('textarea').setValue('测试没有候选')
    await wrapper.find('form.travel-brief').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('信息不足')
    expect(wrapper.find('.save-preview').exists()).toBe(false)
    expect(api.previewAgentConfirmation).not.toHaveBeenCalled()
  })
  it('中断任务缺少结果时展示刷新，不崩溃也不提供保存', async () => {
    vi.mocked(api.createAgentRun).mockResolvedValue({
      ...fixture(),
      status: 'running',
      result: {},
    } as AgentRun)
    const wrapper = mount(AgentWorkspace)
    await flushPromises()
    await wrapper.find('textarea').setValue('检查中断恢复')
    await wrapper.find('form.travel-brief').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('任务正在执行')
    expect(wrapper.text()).toContain('刷新任务状态')
    expect(wrapper.find('.save-preview').exists()).toBe(false)
  })
  it('连续排除候选保留先前排除项，不把旧地点重新放回行程', async () => {
    const first = fixture()
    first.request.excluded_candidate_ids = ['previously-excluded']
    vi.mocked(api.createAgentRun).mockResolvedValue(first)
    vi.mocked(api.editAgentDraft).mockResolvedValue({ ...first, revision: 2 })
    const wrapper = mount(AgentWorkspace)
    await flushPromises()
    await wrapper.find('textarea').setValue('测试连续排除')
    await wrapper.find('form.travel-brief').trigger('submit')
    await flushPromises()
    await wrapper.find('[aria-label="从草案移除夹具地点"]').trigger('click')
    await flushPromises()
    expect(api.editAgentDraft).toHaveBeenCalledWith(
      'test-run',
      expect.objectContaining({ excluded_candidate_ids: ['previously-excluded', 'c1'] }),
    )
  })
})
