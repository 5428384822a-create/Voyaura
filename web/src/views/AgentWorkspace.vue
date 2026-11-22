<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import {
  ArrowLeft,
  ArrowRight,
  BookOpen,
  Check,
  ChevronRight,
  CircleCheck,
  Compass,
  History,
  LoaderCircle,
  MapPin,
  Plus,
  RefreshCw,
  Route,
  ShieldCheck,
  Sparkles,
  Trash2,
} from 'lucide-vue-next'
import { ApiClientError } from '../api/client'
import {
  confirmAgentRun,
  createAgentRun,
  editAgentDraft,
  getAgentCapabilities,
  getAgentRun,
  listAgentRuns,
  previewAgentConfirmation,
} from '../api/agent'
import type {
  AgentCapabilities,
  AgentRun,
  Confirmation,
  RunCreate,
  UserCandidate,
} from '../api/agent'
import AgentRouteMap from '../components/AgentRouteMap.vue'

const props = defineProps<{ initialKind?: 'plan' | 'story'; initialCity?: string }>()
const emit = defineEmits<{ back: []; connect: [] }>()
const mode = ref<'plan' | 'story'>(props.initialKind ?? 'plan')
const cities = [
  { code: '440100', name: '广州市' },
  { code: '330100', name: '杭州市' },
  { code: '310000', name: '上海市' },
  { code: '110000', name: '北京市' },
  { code: '510100', name: '成都市' },
  { code: '350200', name: '厦门市' },
]
const cityCode = ref(props.initialCity ?? '440100')
const goal = ref('')
const localDate = new Date(Date.now() - new Date().getTimezoneOffset() * 60000)
  .toISOString()
  .slice(0, 10)
const startDate = ref(localDate)
const days = ref(2)
const budget = ref<number | ''>('')
const dailyStart = ref('09:00')
const dailyEnd = ref('18:00')
const transport = ref<RunCreate['transport']>('transit')
const pace = ref<RunCreate['pace']>('relaxed')
const interests = ref('')
const mustVisit = ref('')
const allowExternal = ref(false)
const allowModel = ref(false)
const allowMemory = ref(false)
const candidates = ref<
  Array<
    Omit<UserCandidate, 'longitude' | 'latitude'> & {
      longitude: number | ''
      latitude: number | ''
    }
  >
>([])
const capabilities = ref<AgentCapabilities | null>(null)
const history = ref<AgentRun[]>([])
const run = ref<AgentRun | null>(null)
const activeDay = ref(1)
const busy = ref(false)
const error = ref('')
const errorCode = ref('')
const confirmation = ref<Confirmation | null>(null)
const acknowledged = ref(false)
const editTitle = ref('')
const editStory = ref('')
const revisedEnd = ref('18:00')
const pendingRequest = ref<RunCreate | null>(null)
const showHistory = ref(false)
const resultAnchor = ref<HTMLElement | null>(null)
const canSave = computed(
  () =>
    run.value?.status === 'awaiting_confirmation' &&
    !['conflict', 'information_missing'].includes(run.value.result.verification_status),
)
const currentDay = computed(
  () =>
    run.value?.result.days?.find((d) => d.day === activeDay.value) ?? run.value?.result.days?.[0],
)
const statusText = computed(() => {
  if (run.value?.status === 'confirmed') return '已保存到私人档案'
  if (run.value?.status === 'running') return '任务正在执行 · 可稍后刷新'
  if (run.value?.status === 'failed') return '本次整理未完成 · 查看执行记录'
  return {
    validated: '已通过当前约束检查',
    conditional: '条件草案 · 仍需核实',
    conflict: '约束冲突 · 需要调整',
    information_missing: '信息不足 · 请补充',
  }[run.value?.result.verification_status ?? 'information_missing']
})
const sourceLabel = (source: string) => (source === 'amap' ? '高德查询' : '你提供的地点')
function clearConfirmation() {
  confirmation.value = null
  acknowledged.value = false
}
function useRun(value: AgentRun) {
  value = {
    ...value,
    events: value.events ?? [],
    result: {
      ...value.result,
      intent_source: value.result?.intent_source ?? 'local_rules',
      verification_status: value.result?.verification_status ?? 'information_missing',
      summary: value.result?.summary ?? '任务尚无可用结果，请查看执行记录或刷新状态。',
      warnings: value.result?.warnings ?? [],
      unknowns: value.result?.unknowns ?? [],
    },
  }
  run.value = value
  editTitle.value = value.title
  editStory.value = value.result.story_body ?? ''
  revisedEnd.value = String(value.request.daily_end ?? '18:00')
  activeDay.value = value.result.days?.[0]?.day ?? 1
  clearConfirmation()
  void nextTick(() => resultAnchor.value?.scrollIntoView?.({ block: 'start', behavior: 'smooth' }))
}
function reportError(e: unknown) {
  error.value = e instanceof Error ? e.message : '暂时无法完成，请稍后重试。'
  errorCode.value = e instanceof ApiClientError ? e.code : 'CLIENT_ERROR'
}
async function loadHistory() {
  try {
    history.value = (await listAgentRuns()).items
  } catch (e) {
    reportError(e)
  }
}
onMounted(async () => {
  const results = await Promise.allSettled([getAgentCapabilities(), listAgentRuns()])
  if (results[0].status === 'fulfilled') capabilities.value = results[0].value
  if (results[1].status === 'fulfilled') history.value = results[1].value.items
  else reportError(results[1].reason)
})
watch(
  () => props.initialKind,
  (v) => {
    if (v) {
      mode.value = v
      run.value = null
      clearConfirmation()
    }
  },
)
watch(
  () => props.initialCity,
  (v) => {
    if (v) cityCode.value = v
  },
)
watch(mode, () => {
  run.value = null
  error.value = ''
  allowModel.value = false
  allowExternal.value = false
  clearConfirmation()
})
watch(allowExternal, (value) => {
  if (!value) allowModel.value = false
})
function split(value: string) {
  return value
    .split(/[，,、]/)
    .map((s) => s.trim())
    .filter(Boolean)
    .slice(0, 3)
}
function addCandidate() {
  if (candidates.value.length < 12)
    candidates.value.push({
      name: '',
      longitude: '',
      latitude: '',
      stay_minutes: 60,
      cost_yuan: null,
      opening_start: null,
      opening_end: null,
      must_visit: false,
    })
}
function buildRequest(): RunCreate {
  return {
    client_request_id: crypto.randomUUID(),
    kind: mode.value,
    goal: goal.value.trim(),
    city_adcode: cityCode.value,
    city_name: cities.find((c) => c.code === cityCode.value)?.name ?? cityCode.value,
    start_date: startDate.value,
    days: Number(days.value),
    daily_start: dailyStart.value,
    daily_end: dailyEnd.value,
    budget_yuan: budget.value === '' ? null : Number(budget.value),
    transport: transport.value,
    pace: pace.value,
    interests: split(interests.value),
    must_visit: split(mustVisit.value),
    candidates:
      mode.value === 'plan'
        ? candidates.value.map((c) => ({
            ...c,
            longitude: Number(c.longitude),
            latitude: Number(c.latitude),
            stay_minutes: Number(c.stay_minutes),
          }))
        : [],
    allow_external: mode.value === 'plan' && allowExternal.value,
    allow_model: mode.value === 'plan' && allowModel.value,
    allow_memory_access: mode.value === 'story' && allowMemory.value,
    memory_ids: [],
  }
}
async function submit(retry = false) {
  if (busy.value) return
  if (mode.value === 'story' && !allowMemory.value) {
    error.value = '请先授权读取选定城市与日期内的旅行记录。'
    return
  }
  if (!goal.value.trim()) {
    error.value = '先告诉小曦，这次想怎样旅行或整理回忆。'
    return
  }
  const payload = retry && pendingRequest.value ? pendingRequest.value : buildRequest()
  pendingRequest.value = payload
  busy.value = true
  error.value = ''
  errorCode.value = ''
  clearConfirmation()
  try {
    useRun(await createAgentRun(payload))
    pendingRequest.value = null
    await loadHistory()
  } catch (e) {
    reportError(e)
  } finally {
    busy.value = false
  }
}
async function restore(id: string) {
  busy.value = true
  error.value = ''
  try {
    const value = await getAgentRun(id)
    mode.value = value.kind
    await Promise.resolve()
    useRun(value)
    showHistory.value = false
  } catch (e) {
    reportError(e)
  } finally {
    busy.value = false
  }
}
async function editDraft(excluded?: string) {
  if (!run.value || busy.value) return
  busy.value = true
  error.value = ''
  clearConfirmation()
  try {
    const payload =
      run.value.kind === 'story'
        ? {
            expected_revision: run.value.revision,
            title: editTitle.value,
            story_body: editStory.value,
          }
        : {
            expected_revision: run.value.revision,
            daily_end: revisedEnd.value,
            ...(excluded
              ? {
                  excluded_candidate_ids: Array.from(
                    new Set([
                      ...(Array.isArray(run.value.request.excluded_candidate_ids)
                        ? run.value.request.excluded_candidate_ids.filter(
                            (id): id is string => typeof id === 'string',
                          )
                        : []),
                      excluded,
                    ]),
                  ),
                }
              : {}),
          }
    useRun(await editAgentDraft(run.value.id, payload))
    await loadHistory()
  } catch (e) {
    reportError(e)
  } finally {
    busy.value = false
  }
}
async function previewSave() {
  if (!run.value) return
  busy.value = true
  error.value = ''
  try {
    confirmation.value = await previewAgentConfirmation(run.value)
    acknowledged.value = false
  } catch (e) {
    reportError(e)
  } finally {
    busy.value = false
  }
}
async function save() {
  if (!run.value || !confirmation.value) return
  busy.value = true
  error.value = ''
  try {
    useRun(await confirmAgentRun(run.value, confirmation.value, acknowledged.value))
    await loadHistory()
  } catch (e) {
    reportError(e)
  } finally {
    busy.value = false
  }
}
function eventLabel(status: string) {
  return (
    (
      {
        success: '完成',
        succeeded: '完成',
        failed: '未完成',
        error: '失败',
        started: '开始',
        retrying: '重试',
        skipped: '跳过',
        warning: '需留意',
        running: '执行中',
      } as Record<string, string>
    )[status] ?? status
  )
}
</script>

<template>
  <main class="agent-workspace">
    <header class="workspace-header">
      <div class="workspace-heading">
        <button class="icon-button" type="button" aria-label="返回旅行地图" @click="emit('back')">
          <ArrowLeft :size="19" />
        </button>
        <div>
          <p class="eyebrow">VOYAURA · WITH XIAOXI</p>
          <h1>小曦旅行手记</h1>
        </div>
      </div>
      <div class="workspace-header-actions">
        <span class="private-badge"><ShieldCheck :size="15" />私人档案</span
        ><button class="text-button" type="button" @click="showHistory = !showHistory">
          <History :size="17" />最近任务 <span>{{ history.length }}</span>
        </button>
      </div>
    </header>
    <div class="workspace-scroll">
      <div v-if="showHistory" class="history-strip">
        <div>
          <strong>接着上次的旅程</strong
          ><button type="button" class="text-button" @click="loadHistory">
            <RefreshCw :size="14" />刷新
          </button>
        </div>
        <p v-if="!history.length">还没有任务。第一段旅程，从下面开始。</p>
        <button
          v-for="item in history"
          :key="item.id"
          type="button"
          :disabled="busy"
          @click="restore(item.id)"
        >
          <span>{{ item.kind === 'plan' ? '行程' : '故事' }} · {{ item.title }}</span
          ><small
            >{{ item.status === 'confirmed' ? '已保存' : '草稿' }} · 第{{ item.revision }}版</small
          ><ChevronRight :size="16" />
        </button>
      </div>
      <div class="workspace-grid">
        <aside class="brief-column">
          <div class="brief-intro">
            <span class="companion-seal"><Sparkles :size="22" /></span>
            <p class="eyebrow">PLAN THE JOURNEY. SHAPE THE STORY.</p>
            <h2>
              {{
                mode === 'plan' ? '想去的地方，\n一起慢慢安排。' : '走过的旅途，\n值得好好记住。'
              }}
            </h2>
            <p>
              {{
                mode === 'plan'
                  ? '你说想法，我整理地点、每天的节奏和需要核实的细节。'
                  : '从你留下的日期、文字和影像数量出发，整理成可编辑的旅行故事。'
              }}
            </p>
          </div>
          <div class="mode-switch" role="group" aria-label="任务类型">
            <button :class="{ active: mode === 'plan' }" type="button" @click="mode = 'plan'">
              <Compass :size="16" />规划旅程</button
            ><button :class="{ active: mode === 'story' }" type="button" @click="mode = 'story'">
              <BookOpen :size="16" />整理故事
            </button>
          </div>
          <form class="travel-brief" @submit.prevent="submit(false)">
            <label class="field"
              ><span>{{ mode === 'plan' ? '这次想怎样旅行？' : '想留下一段怎样的回忆？' }}</span
              ><textarea
                v-model="goal"
                required
                minlength="2"
                maxlength="1500"
                rows="3"
                :placeholder="
                  mode === 'plan'
                    ? '想轻松逛两天，喜欢博物馆和街巷，下午留点时间休息…'
                    : '把这几天的旅行日记整理成一段故事，保留当时写下的细节…'
                "
              ></textarea>
            </label>
            <div class="field-pair">
              <label class="field"
                ><span>目的地</span
                ><select v-model="cityCode">
                  <option v-for="city in cities" :key="city.code" :value="city.code">
                    {{ city.name }}
                  </option>
                  <option v-if="!cities.some((c) => c.code === cityCode)" :value="cityCode">
                    城市 {{ cityCode }}
                  </option>
                </select></label
              ><label class="field"
                ><span>{{ mode === 'plan' ? '出发日期' : '回忆开始日期' }}</span
                ><input v-model="startDate" type="date" required
              /></label>
            </div>
            <div class="field-pair">
              <label class="field"
                ><span>{{ mode === 'plan' ? '旅行天数' : '回忆时间范围' }}</span
                ><select v-model.number="days">
                  <option v-for="n in 4" :key="n" :value="n">{{ n }} 天</option>
                </select></label
              ><label v-if="mode === 'plan'" class="field"
                ><span>景点预算 / 元</span
                ><input v-model="budget" type="number" min="0" max="1000000" placeholder="暂不限定"
              /></label>
            </div>
            <template v-if="mode === 'plan'">
              <div class="field-pair">
                <label class="field"
                  ><span>每天开始</span><input v-model="dailyStart" type="time" required /></label
                ><label class="field"
                  ><span>每天结束</span><input v-model="dailyEnd" type="time" required
                /></label>
              </div>
              <div class="field-pair">
                <label class="field"
                  ><span>出行方式</span
                  ><select v-model="transport">
                    <option value="transit">公交 / 地铁</option>
                    <option value="walking">步行</option>
                    <option value="driving">驾车</option>
                  </select></label
                ><label class="field"
                  ><span>旅行节奏</span
                  ><select v-model="pace">
                    <option value="relaxed">慢一点，留些空白</option>
                    <option value="balanced">均衡安排</option>
                  </select></label
                >
              </div>
              <label class="field"
                ><span>想逛什么 <small>最多3项，逗号分隔</small></span
                ><input v-model="interests" maxlength="240" placeholder="博物馆，公园，历史街区"
              /></label>
              <label class="field"
                ><span>一定想去 <small>可选，最多3项</small></span
                ><input v-model="mustVisit" maxlength="240" placeholder="填写具体地点名称"
              /></label>
              <details class="candidate-input" :open="!capabilities?.amap_configured">
                <summary>
                  <MapPin :size="15" />我已有想去的地点 <span>{{ candidates.length }}</span>
                </summary>
                <p>可填你掌握的地点与GCJ-02坐标。系统会注明“你提供”，未经地图核验。</p>
                <fieldset v-for="(candidate, index) in candidates" :key="index">
                  <legend>地点 {{ index + 1 }}</legend>
                  <button
                    class="remove-candidate"
                    type="button"
                    :aria-label="`移除地点${index + 1}`"
                    @click="candidates.splice(index, 1)"
                  >
                    <Trash2 :size="14" /></button
                  ><label class="field"
                    ><span>地点名称</span
                    ><input
                      v-model="candidate.name"
                      required
                      maxlength="100"
                      placeholder="填写真实地点名称"
                  /></label>
                  <div class="field-pair">
                    <label class="field"
                      ><span>GCJ-02经度</span
                      ><input
                        v-model.number="candidate.longitude"
                        type="number"
                        required
                        step="any"
                        min="73"
                        max="136" /></label
                    ><label class="field"
                      ><span>GCJ-02纬度</span
                      ><input
                        v-model.number="candidate.latitude"
                        type="number"
                        required
                        step="any"
                        min="3"
                        max="54"
                    /></label>
                  </div>
                  <div class="field-pair">
                    <label class="field"
                      ><span>停留 / 分钟</span
                      ><input
                        v-model.number="candidate.stay_minutes"
                        type="number"
                        min="15"
                        max="480"
                        required /></label
                    ><label class="field"
                      ><span>已知票价 / 元</span
                      ><input
                        v-model="candidate.cost_yuan"
                        type="number"
                        min="0"
                        step="0.01"
                        placeholder="未知"
                        @change="
                          candidate.cost_yuan =
                            candidate.cost_yuan === null || String(candidate.cost_yuan) === ''
                              ? null
                              : Number(candidate.cost_yuan)
                        "
                    /></label>
                  </div>
                  <div class="field-pair">
                    <label class="field"
                      ><span>开放时间（可选）</span
                      ><input
                        v-model="candidate.opening_start"
                        type="time"
                        @change="candidate.opening_start ||= null" /></label
                    ><label class="field"
                      ><span>闭馆时间（可选）</span
                      ><input
                        v-model="candidate.opening_end"
                        type="time"
                        @change="candidate.opening_end ||= null"
                    /></label>
                  </div>
                  <label class="consent compact"
                    ><input v-model="candidate.must_visit" type="checkbox" /><span
                      >这是必去地点</span
                    ></label
                  >
                </fieldset>
                <button
                  class="text-button"
                  type="button"
                  :disabled="candidates.length >= 12"
                  @click="addCandidate"
                >
                  <Plus :size="15" />添加地点
                </button>
              </details>
              <label class="consent"
                ><input v-model="allowExternal" type="checkbox" /><span
                  >允许查询高德地点与路线<small
                    >会向高德发送目的地、地点和出行方式，可能消耗服务额度。{{
                      capabilities?.amap_configured ? '' : '当前服务尚未配置地图查询。'
                    }}</small
                  ></span
                ></label
              >
              <label v-if="capabilities?.model_configured" class="consent"
                ><input v-model="allowModel" type="checkbox" :disabled="!allowExternal" /><span
                  >允许模型辅助理解本次需求<small
                    >只发送当前旅行需求，可能产生模型费用；不发送私人记忆。</small
                  ></span
                ></label
              >
            </template>
            <label v-else class="consent"
              ><input v-model="allowMemory" type="checkbox" required /><span
                >允许读取所选城市与日期的私人记录<small
                  >仅在本服务内整理文字、日期和可用影像数量；不读取照片内容、不向外部传输。</small
                ></span
              ></label
            >
            <button class="primary-action" type="submit" :disabled="busy">
              <LoaderCircle v-if="busy" class="spin" :size="18" /><Sparkles v-else :size="18" />{{
                busy ? '小曦正在整理…' : mode === 'plan' ? '一起安排这段旅程' : '整理我的旅行故事'
              }}<ArrowRight v-if="!busy" :size="17" />
            </button>
            <p class="brief-footnote">
              所有结果先成为草案，确认后才保存。不会自动购买、公开发布或点亮城市。
            </p>
          </form>
        </aside>
        <section
          ref="resultAnchor"
          class="result-column"
          aria-live="polite"
          aria-label="小曦执行结果"
        >
          <div v-if="error" class="workspace-error" role="alert">
            <strong>{{ error }}</strong
            ><small v-if="errorCode">{{ errorCode }}</small
            ><button
              v-if="errorCode.includes('AUTH') || errorCode === 'HTTP_401'"
              class="text-button"
              type="button"
              @click="emit('connect')"
            >
              连接私人档案</button
            ><button
              v-else-if="pendingRequest"
              class="text-button"
              type="button"
              :disabled="busy"
              @click="submit(true)"
            >
              重试同一任务
            </button>
          </div>
          <div v-if="busy && !run" class="result-empty">
            <LoaderCircle class="spin" :size="36" />
            <h2>把想法，慢慢落到地图上。</h2>
            <p>正在核对输入、执行已授权工具并检查约束。结果与调用记录会一起保留。</p>
          </div>
          <div v-else-if="!run" class="result-empty">
            <div class="empty-atlas">
              <Compass :size="64" :stroke-width="1" /><span>YOUR NEXT CHAPTER</span>
            </div>
            <p class="eyebrow">TRAVEL WITH INTENTION</p>
            <h2>旅途有方向，<br />也有属于你的留白。</h2>
            <p>写下愿望，补上已知地点。小曦会把每天的安排、信息来源与尚待核实的地方放在一起。</p>
            <div class="promise-row">
              <span><Route :size="17" />可编辑日程</span
              ><span><ShieldCheck :size="17" />来源可追溯</span
              ><span><Check :size="17" />由你确认</span>
            </div>
          </div>
          <template v-else>
            <header class="result-heading">
              <div>
                <p class="eyebrow">
                  {{ run.kind === 'plan' ? 'YOUR JOURNEY, IN THE MAKING' : 'YOUR TRAVEL STORY' }}
                </p>
                <h2>{{ run.title }}</h2>
              </div>
              <span class="revision-label">版本 {{ run.revision }}</span>
            </header>
            <div class="result-status" :class="run.result.verification_status">
              <CircleCheck :size="18" /><strong>{{ statusText }}</strong
              ><span>{{
                run.result.intent_source === 'deepseek' ? '模型辅助理解' : '本地规则整理'
              }}</span>
            </div>
            <p class="result-summary">{{ run.result.summary }}</p>
            <button
              v-if="run.status === 'running'"
              class="secondary-action"
              type="button"
              :disabled="busy"
              @click="restore(run.id)"
            >
              <RefreshCw :size="15" />刷新任务状态
            </button>
            <template v-if="run.kind === 'plan' && run.result.days?.length">
              <AgentRouteMap
                :days="run.result.days"
                :active-day="activeDay"
                :allow-external="run.request.allow_external === true"
              />
              <div class="day-tabs" role="group" aria-label="每日行程">
                <button
                  v-for="day in run.result.days"
                  :key="day.day"
                  type="button"
                  :class="{ active: activeDay === day.day }"
                  :aria-pressed="activeDay === day.day"
                  @click="activeDay = day.day"
                >
                  <small>DAY {{ String(day.day).padStart(2, '0') }}</small
                  ><strong>{{ day.date.slice(5).replace('-', ' / ') }}</strong
                  ><span>{{ day.stops.length }} 个地点</span>
                </button>
              </div>
              <ol v-if="currentDay" class="day-timeline">
                <li v-for="(stop, index) in currentDay.stops" :key="stop.candidate_id">
                  <div class="stop-time">
                    <strong>{{ stop.arrival }}</strong
                    ><small>{{ stop.departure }}</small>
                  </div>
                  <span class="stop-dot">{{ index + 1 }}</span>
                  <article>
                    <div>
                      <h3>{{ stop.name }}</h3>
                      <button
                        v-if="run.status !== 'confirmed'"
                        class="text-button"
                        type="button"
                        :disabled="busy"
                        :aria-label="`从草案移除${stop.name}`"
                        @click="editDraft(stop.candidate_id)"
                      >
                        移除
                      </button>
                    </div>
                    <p>
                      <span>{{ sourceLabel(stop.source) }}</span> · 停留
                      {{ stop.stay_minutes }} 分钟
                    </p>
                    <small v-if="stop.timing_basis === 'planning_buffer'"
                      >时间含规划预留，交通尚需核实</small
                    ><small v-else>{{
                      index === 0 ? '按你设置的开始时间安排' : '按已查询交通时间安排'
                    }}</small>
                  </article>
                </li>
                <li v-if="!currentDay.stops.length" class="empty-day">
                  这一天还没有安排地点，可继续补充。
                </li>
              </ol>
              <div v-if="run.result.validation" class="budget-summary">
                <strong>已知景点费用 ¥{{ run.result.validation.known_cost_yuan }}</strong
                ><span
                  >{{ run.result.validation.unknown_cost_count }} 项票价未知 ·
                  不含住宿、餐饮与交通</span
                >
              </div>
              <form
                v-if="run.status !== 'confirmed'"
                class="replan-form"
                @submit.prevent="editDraft()"
              >
                <label>想早点结束？<input v-model="revisedEnd" type="time" required /></label
                ><button class="secondary-action" type="submit" :disabled="busy">
                  重新安排并检查
                </button>
              </form>
            </template>
            <template v-if="run.kind === 'story' && run.result.story_body">
              <div class="story-paper">
                <p class="eyebrow">FIELD NOTES · A PRIVATE STORY</p>
                <label
                  ><span>故事标题</span
                  ><input
                    v-model="editTitle"
                    maxlength="160"
                    :readonly="run.status === 'confirmed'" /></label
                ><label
                  ><span>你的旅行故事</span
                  ><textarea
                    v-model="editStory"
                    maxlength="16000"
                    :readonly="run.status === 'confirmed'"
                    rows="14"
                  ></textarea></label
                ><button
                  v-if="run.status !== 'confirmed'"
                  class="secondary-action"
                  type="button"
                  :disabled="busy"
                  @click="editDraft()"
                >
                  保存草稿修改并重新检查</button
                ><small>{{
                  run.status === 'confirmed'
                    ? '已保存为独立私有快照；删除原记忆不会同步删除此故事。'
                    : '确认前请先保存你的修改。手动添加内容由你核实。'
                }}</small>
              </div>
              <details class="source-records">
                <summary>查看 {{ run.result.source_memories?.length ?? 0 }} 条原始旅行记录</summary>
                <article v-for="memory in run.result.source_memories" :key="memory.id">
                  <small>{{ memory.date }} · {{ memory.city }}</small
                  ><strong>{{ memory.title }}</strong>
                  <p>{{ memory.body }}</p>
                  <span>{{ memory.photo_count }} 张可用照片 · {{ memory.vlog_count }} 段Vlog</span>
                </article>
              </details>
            </template>
            <section
              v-if="run.result.unknowns.length || run.result.warnings.length"
              class="unknown-card"
            >
              <h3>{{ run.kind === 'story' ? '保存前，再确认这些' : '出发前，再确认这些' }}</h3>
              <ul>
                <li v-for="(item, i) in [...run.result.unknowns, ...run.result.warnings]" :key="i">
                  {{ item }}
                </li>
              </ul>
            </section>
            <details v-if="run.result.validation?.checks.length" class="validation-card">
              <summary><ShieldCheck :size="16" />查看约束检查</summary>
              <p v-for="(item, i) in run.result.validation.checks" :key="i">
                <span :class="item.status">{{ item.status }}</span
                >{{ item.message }}
              </p>
            </details>
            <section class="execution-card">
              <header>
                <div>
                  <p class="eyebrow">A TRACEABLE JOURNEY</p>
                  <h3>小曦做了什么</h3>
                </div>
                <small>{{ run.events.length }} 条执行记录</small>
              </header>
              <ol>
                <li v-for="event in run.events" :key="event.sequence">
                  <span class="event-dot" :class="event.status"></span>
                  <div>
                    <p>{{ event.message }}</p>
                    <small
                      >{{ event.tool }} · {{ eventLabel(event.status)
                      }}<template v-if="event.attempt > 1">
                        · 第{{ event.attempt }}次尝试</template
                      ></small
                    >
                    <details v-if="event.details && Object.keys(event.details).length">
                      <summary>调用详情</summary>
                      <pre>{{ JSON.stringify(event.details, null, 2) }}</pre>
                    </details>
                  </div>
                </li>
              </ol>
            </section>
            <div v-if="run.status === 'confirmed'" class="saved-card" role="status">
              <CircleCheck :size="24" />
              <div>
                <strong>这段{{ run.kind === 'plan' ? '旅程' : '故事' }}，已妥善收藏。</strong>
                <p>保存在你的私人档案，可从“最近任务”重新打开。</p>
              </div>
            </div>
            <section
              v-else-if="confirmation"
              class="confirmation-card"
              role="region"
              aria-label="确认保存草案"
            >
              <h3>把当前版本存入私人档案？</h3>
              <p>{{ confirmation.summary }}</p>
              <p v-if="run.kind === 'story'">
                保存后将形成独立故事副本；之后删除原记忆不会同步删除此副本。
              </p>
              <small
                >第 {{ confirmation.revision }} 版 · 确认有效至
                {{ new Date(confirmation.expires_at).toLocaleTimeString('zh-CN') }}</small
              ><label v-if="confirmation.requires_unverified_acknowledgement" class="consent"
                ><input v-model="acknowledged" type="checkbox" /><span>{{
                  run.kind === 'story'
                    ? '我了解记录和编辑内容未经独立事实核验，按条件草案保存。'
                    : '我了解仍有未核实信息，按条件草案保存，出行前自行确认。'
                }}</span></label
              >
              <div>
                <button
                  class="secondary-action"
                  type="button"
                  :disabled="busy"
                  @click="clearConfirmation"
                >
                  再看看</button
                ><button
                  class="primary-action"
                  type="button"
                  :disabled="
                    busy || (confirmation.requires_unverified_acknowledgement && !acknowledged)
                  "
                  @click="save"
                >
                  {{ busy ? '正在保存…' : '确认保存到私人档案' }}
                </button>
              </div>
            </section>
            <button
              v-else-if="canSave"
              class="primary-action save-preview"
              type="button"
              :disabled="
                busy ||
                (run.kind === 'story' &&
                  (editTitle !== run.title || editStory !== run.result.story_body))
              "
              @click="previewSave"
            >
              <ShieldCheck :size="18" />核对并保存当前草案<ArrowRight :size="17" />
            </button>
            <p v-else class="save-blocked">补齐信息或解决冲突后，才能保存草案。</p>
          </template>
        </section>
      </div>
    </div>
  </main>
</template>

<style scoped>
.agent-workspace {
  position: absolute;
  inset: 0 0 0 78px;
  display: flex;
  flex-direction: column;
  background: #f5f2e9;
  color: #2d3831;
  overflow: hidden;
}
.workspace-header {
  height: 90px;
  min-height: 90px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 36px;
  border-bottom: 1px solid #dcd9cd;
  background: #fbf8f0;
}
.workspace-heading {
  display: flex;
  gap: 15px;
  align-items: center;
}
.workspace-heading h1 {
  font-size: 21px;
  letter-spacing: -0.7px;
  margin: 5px 0;
}
.icon-button {
  display: grid;
  place-items: center;
  width: 35px;
  height: 35px;
  border: 1px solid #d7d6cb;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
}
.workspace-header-actions {
  display: flex;
  gap: 20px;
  align-items: center;
}
.private-badge {
  display: flex;
  gap: 6px;
  color: #6d7d67;
  font-size: 11px;
}
.text-button {
  display: inline-flex;
  gap: 5px;
  align-items: center;
  padding: 5px 0;
  border: 0;
  background: transparent;
  color: #626f60;
  font-size: 11px;
  cursor: pointer;
}
.text-button:disabled {
  opacity: 0.4;
  cursor: wait;
}
.workspace-scroll {
  flex: 1;
  overflow: auto;
}
.workspace-grid {
  display: grid;
  grid-template-columns: minmax(280px, 340px) minmax(0, 1fr);
  max-width: 1400px;
  margin: 0 auto;
  align-items: start;
}
.brief-column {
  padding: 34px 28px;
  border-right: 1px solid #ddded0;
}
.companion-seal {
  display: grid;
  place-items: center;
  width: 43px;
  height: 43px;
  margin-bottom: 20px;
  background: #efe4cf;
  border-radius: 50%;
  color: #ac6c2d;
}
.brief-intro .eyebrow {
  font-size: 8px;
  letter-spacing: 1.3px;
  color: #82735b;
}
.brief-intro h2 {
  white-space: pre-line;
  font-family: 'Source Serif 4', 'Microsoft YaHei', serif;
  font-size: 26px;
  line-height: 1.5;
  letter-spacing: -1px;
  margin: 10px 0;
}
.brief-intro > p:last-child {
  font-size: 12px;
  line-height: 1.9;
  color: #737d70;
}
.mode-switch {
  display: flex;
  border: 1px solid #d8d9cd;
  padding: 4px;
  border-radius: 9px;
  margin: 23px 0;
  background: #eaece1;
}
.mode-switch button {
  flex: 1;
  display: flex;
  gap: 6px;
  align-items: center;
  justify-content: center;
  padding: 9px 3px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  font-size: 11px;
  color: #78816f;
  cursor: pointer;
}
.mode-switch button.active {
  background: #fffdf5;
  color: #3b5546;
  box-shadow: 0 2px 5px #4d5e4312;
}
.travel-brief {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
  min-width: 0;
}
.field > span {
  display: flex;
  justify-content: space-between;
  gap: 5px;
  font-size: 11px;
  font-weight: 600;
  line-height: 1.5;
}
.field small {
  font-size: 9px;
  font-weight: 400;
  color: #929587;
}
.field input,
.field textarea,
.field select {
  width: 100%;
  min-width: 0;
  padding: 10px 9px;
  border: 1px solid #d5d6c9;
  border-radius: 6px;
  color: #3c463d;
  background: #fcfbf4;
  font: 12px/1.7 inherit;
  outline-offset: 2px;
}
.field textarea {
  resize: vertical;
  min-height: 94px;
}
.field input:focus,
.field textarea:focus,
.field select:focus {
  border-color: #849c7d;
  outline: 2px solid #879d7830;
}
.field-pair {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.candidate-input {
  padding: 13px;
  border: 1px dashed #bdc8b5;
  border-radius: 8px;
  background: #edf0e4;
}
.candidate-input summary {
  display: flex;
  gap: 6px;
  align-items: center;
  cursor: pointer;
  font-size: 11px;
  font-weight: 600;
}
.candidate-input summary span {
  margin-left: auto;
  color: #8c927e;
}
.candidate-input > p {
  font-size: 10px;
  line-height: 1.8;
  color: #78816d;
}
.candidate-input fieldset {
  position: relative;
  min-width: 0;
  margin: 14px 0;
  padding: 10px;
  border: 1px solid #d0d6c5;
  border-radius: 6px;
}
.candidate-input legend {
  font-size: 10px;
  color: #7a866d;
}
.candidate-input .field {
  margin: 6px 0;
}
.candidate-input .field-pair {
  gap: 6px;
}
.candidate-input .field > span {
  font-size: 9px;
}
.candidate-input .field input {
  padding: 7px;
  font-size: 11px;
}
.remove-candidate {
  position: absolute;
  right: 5px;
  top: -13px;
  border: 0;
  background: #edf0e4;
  color: #956b57;
  cursor: pointer;
}
.consent {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 11px;
  line-height: 1.7;
  color: #57684e;
  cursor: pointer;
}
.consent input {
  accent-color: #587955;
  width: 15px;
  height: 15px;
  min-width: 15px;
  margin: 2px 0;
}
.consent small {
  display: block;
  font-size: 9px;
  line-height: 1.8;
  color: #909480;
}
.consent.compact {
  font-size: 10px;
}
.primary-action,
.secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 42px;
  padding: 11px 15px;
  border: 0;
  border-radius: 7px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  line-height: 1.5;
}
.primary-action {
  background: #e9583e;
  color: #fffaf1;
  box-shadow: 0 4px 10px #ad4c2a12;
}
.primary-action svg:last-child {
  margin-left: auto;
}
.primary-action:disabled,
.secondary-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.secondary-action {
  border: 1px solid #cbd2bd;
  background: #fafaf0;
  color: #506344;
}
.brief-footnote {
  font-size: 9px;
  line-height: 1.9;
  text-align: center;
  color: #969a89;
  margin: 0;
}
.result-column {
  padding: 32px 36px 45px;
  min-width: 0;
}
.result-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 620px;
  text-align: center;
}
.empty-atlas {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  width: 220px;
  height: 220px;
  margin: 5px 0 40px;
  border: 1px solid #cdd4bd;
  border-radius: 50%;
  background: radial-gradient(ellipse, #e7eddd, #f4f3e9 70%);
  color: #7c9470;
}
.empty-atlas:after {
  position: absolute;
  content: '';
  inset: 14px;
  border: 1px dashed #cbd4bc;
  border-radius: 50%;
}
.empty-atlas > span {
  font-size: 8px;
  letter-spacing: 2.3px;
}
.result-empty h2 {
  font-family: 'Microsoft YaHei', serif;
  font-weight: 500;
  font-size: 29px;
  line-height: 1.6;
  letter-spacing: 1px;
  margin: 17px 0;
}
.result-empty > p:not(.eyebrow) {
  max-width: 350px;
  color: #8a907e;
  font-size: 12px;
  line-height: 2;
}
.promise-row {
  display: flex;
  gap: 22px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 27px;
}
.promise-row span {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  color: #7d8d6e;
}
.result-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}
.result-heading h2 {
  margin: 8px 0 18px;
  font-size: 24px;
  line-height: 1.6;
  letter-spacing: -0.6px;
}
.revision-label {
  white-space: nowrap;
  padding: 5px 8px;
  border: 1px solid #d9dccb;
  border-radius: 4px;
  color: #8c917f;
  font-size: 10px;
}
.result-status {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px;
  border: 1px solid #ddcfb1;
  border-radius: 7px;
  background: #f3eddc;
  color: #92713d;
  font-size: 11px;
}
.result-status > span {
  margin-left: auto;
  color: #8d917e;
  font-size: 9px;
}
.result-status.validated {
  color: #4b754f;
  border-color: #bdcdb3;
  background: #e7edde;
}
.result-status.conflict {
  color: #ae533c;
  border-color: #ddbcaa;
  background: #f3e7dc;
}
.result-summary {
  margin: 15px 0 20px;
  font-size: 12px;
  line-height: 2;
  color: #79806e;
  white-space: pre-line;
}
.day-tabs {
  display: flex;
  gap: 8px;
  margin: 18px 0;
}
.day-tabs button {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  flex: 1;
  min-width: 0;
  padding: 13px;
  border: 1px solid #dbdecd;
  border-radius: 7px;
  background: #f9f8f0;
  color: #838c78;
  cursor: pointer;
}
.day-tabs button.active {
  border-color: #829e75;
  color: #46653b;
  background: #edf1e2;
}
.day-tabs small {
  font-size: 8px;
  letter-spacing: 1px;
}
.day-tabs strong {
  font-size: 13px;
}
.day-tabs span {
  font-size: 9px;
  color: #8d977f;
}
.day-timeline {
  list-style: none;
  margin: 24px 0;
  padding: 0;
}
.day-timeline > li {
  position: relative;
  display: grid;
  grid-template-columns: 42px 24px 1fr;
  gap: 12px;
  padding-bottom: 23px;
}
.day-timeline > li:not(:last-child):after {
  position: absolute;
  content: '';
  width: 1px;
  left: 66px;
  top: 24px;
  bottom: 0;
  background: #d7deca;
}
.stop-time {
  display: flex;
  flex-direction: column;
  gap: 7px;
  font-size: 11px;
}
.stop-time small {
  color: #9b9e8c;
  font-size: 9px;
}
.stop-dot {
  display: grid;
  place-items: center;
  position: relative;
  z-index: 1;
  height: 24px;
  border-radius: 50%;
  border: 1px solid #d2d9c3;
  background: #faf9ef;
  color: #7b8b67;
  font-size: 10px;
}
.day-timeline article > div {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.day-timeline h3 {
  font-size: 14px;
  margin: 0;
}
.day-timeline article p {
  margin: 8px 0 5px;
  font-size: 10px;
  color: #8c937d;
}
.day-timeline article p span {
  border: 1px solid #d9deca;
  border-radius: 3px;
  padding: 2px 4px;
  font-size: 9px;
}
.day-timeline article > small {
  font-size: 9px;
  color: #a2916c;
}
.empty-day {
  display: block !important;
  padding: 20px;
  color: #929681;
  font-size: 12px;
}
.budget-summary {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 0;
  border-top: 1px solid #dedfcf;
  font-size: 11px;
}
.budget-summary span {
  font-size: 9px;
  color: #8d937e;
}
.replan-form {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin: 14px 0 20px;
  padding: 12px;
  background: #edeedf;
  border-radius: 7px;
}
.replan-form label {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 10px;
}
.replan-form input {
  max-width: 100px;
  border: 1px solid #cbd1ba;
  border-radius: 4px;
  padding: 5px;
  background: #faf9ee;
  font-size: 11px;
}
.replan-form button {
  min-height: 32px;
  padding: 7px 9px;
  font-size: 10px;
}
.unknown-card {
  margin: 22px 0;
  padding: 17px 18px;
  border-left: 3px solid #c1a56a;
  background: #efeada;
}
.unknown-card h3 {
  font-size: 12px;
  margin: 0 0 10px;
  color: #817347;
}
.unknown-card ul {
  padding-left: 16px;
  margin: 0;
}
.unknown-card li {
  margin: 7px 0;
  color: #908467;
  font-size: 10px;
  line-height: 1.9;
}
.validation-card {
  margin: 18px 0;
  border: 1px solid #dadfcb;
  border-radius: 7px;
  padding: 13px;
}
.validation-card summary {
  display: flex;
  gap: 7px;
  align-items: center;
  cursor: pointer;
  font-size: 11px;
  color: #768567;
}
.validation-card p {
  display: flex;
  gap: 8px;
  font-size: 10px;
  color: #899276;
  line-height: 1.7;
}
.validation-card p span {
  font-size: 9px;
}
.execution-card {
  margin-top: 24px;
  padding: 20px;
  border: 1px solid #dcdccc;
  border-radius: 10px;
  background: #f9f8ef;
}
.execution-card > header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.execution-card h3 {
  font-size: 14px;
  margin: 5px 0 18px;
}
.execution-card header > small {
  font-size: 10px;
  color: #8d957d;
}
.execution-card .eyebrow {
  font-size: 8px;
  letter-spacing: 1.2px;
  color: #9a967c;
}
.execution-card ol {
  padding: 0;
  list-style: none;
  margin: 5px 0 0;
  max-height: 350px;
  overflow: auto;
}
.execution-card li {
  display: flex;
  gap: 12px;
  padding: 9px 0;
}
.event-dot {
  width: 7px;
  height: 7px;
  min-width: 7px;
  margin-top: 4px;
  background: #9ba58b;
  border-radius: 50%;
}
.event-dot.failed,
.event-dot.error {
  background: #ca8064;
}
.event-dot.success,
.event-dot.succeeded {
  background: #6f9765;
}
.execution-card li p {
  font-size: 10px;
  line-height: 1.8;
  margin: 0;
  color: #79846a;
}
.execution-card li small {
  font-size: 9px;
  color: #a2a68e;
}
.execution-card details {
  margin-top: 7px;
  color: #959c81;
  font-size: 9px;
}
.execution-card details pre {
  max-width: 100%;
  overflow: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.execution-card summary {
  cursor: pointer;
}
.save-preview {
  display: flex;
  width: 100%;
  margin-top: 22px;
}
.confirmation-card {
  margin-top: 22px;
  padding: 20px;
  border: 1px solid #adbd9b;
  border-radius: 10px;
  background: #edf1e0;
}
.confirmation-card h3 {
  font-size: 14px;
  margin: 0 0 10px;
}
.confirmation-card p {
  font-size: 11px;
  line-height: 1.9;
  color: #6f7d5b;
}
.confirmation-card > small {
  font-size: 10px;
  color: #8a9875;
}
.confirmation-card .consent {
  margin: 18px 0;
}
.confirmation-card > div {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}
.confirmation-card > div .primary-action {
  box-shadow: none;
}
.saved-card {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 20px;
  padding: 19px;
  border: 1px solid #c5d1b4;
  border-radius: 8px;
  background: #e7eddb;
  color: #5c784b;
}
.saved-card strong {
  font-size: 13px;
}
.saved-card p {
  font-size: 10px;
  margin: 7px 0 0;
  color: #879774;
}
.save-blocked {
  text-align: center;
  font-size: 11px;
  line-height: 1.8;
  color: #a6936a;
  padding: 15px;
}
.workspace-error {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: #f0e0d5;
  border: 1px solid #dcb49d;
  border-radius: 7px;
  color: #9c543d;
  font-size: 12px;
  margin-bottom: 20px;
}
.workspace-error small {
  font-size: 10px;
}
.workspace-error button {
  align-self: flex-start;
  color: #ac6444;
}
.story-paper {
  padding: 25px;
  background: #fffaf0;
  border: 1px solid #ddd6be;
  box-shadow: 0 8px 20px #74734808;
}
.story-paper > label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 16px 0;
}
.story-paper label > span {
  font-size: 10px;
  color: #a2987a;
}
.story-paper input,
.story-paper textarea {
  width: 100%;
  background: transparent;
  border: 0;
  border-bottom: 1px solid #e3dcc7;
  padding: 8px 0;
  resize: vertical;
  color: #5d624f;
  line-height: 2;
  font-size: 13px;
  white-space: pre-wrap;
}
.story-paper input {
  font-size: 20px;
  font-weight: 600;
}
.story-paper > small {
  display: block;
  margin-top: 12px;
  font-size: 10px;
  color: #a39a7f;
}
.source-records {
  margin: 18px 0;
  padding: 16px;
  border: 1px solid #dfdecb;
  border-radius: 8px;
  font-size: 11px;
  color: #7a836c;
}
.source-records summary {
  cursor: pointer;
}
.source-records article {
  padding: 15px 0;
  border-bottom: 1px solid #e2e2d0;
}
.source-records article strong,
.source-records article small {
  display: block;
  margin: 6px 0;
}
.source-records p {
  white-space: pre-wrap;
  line-height: 1.9;
  font-size: 11px;
}
.source-records article span,
.source-records article small {
  font-size: 9px;
  color: #a0a48b;
}
.history-strip {
  margin: 22px 28px 0;
  padding: 18px;
  border: 1px solid #d6ddc5;
  border-radius: 10px;
  background: #edf1e2;
}
.history-strip > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
}
.history-strip > button {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  text-align: left;
  border: 0;
  border-bottom: 1px solid #d8dfc8;
  background: transparent;
  cursor: pointer;
  font-size: 11px;
  color: #6d7a59;
}
.history-strip > button small {
  margin-left: auto;
  font-size: 10px;
  color: #9aa486;
}
.history-strip > p {
  font-size: 11px;
  color: #8d997b;
}
@media (min-width: 1440px) {
  .brief-column {
    padding: 40px 30px;
  }
  .workspace-grid {
    grid-template-columns: 360px minmax(0, 1fr);
  }
  .result-column {
    padding: 40px 48px;
  }
  .result-empty {
    min-height: 690px;
  }
}
@media (max-width: 1000px) {
  .workspace-header {
    padding: 0 22px;
  }
  .workspace-grid {
    grid-template-columns: minmax(260px, 310px) minmax(0, 1fr);
  }
  .brief-column {
    padding: 25px 20px;
  }
  .result-column {
    padding: 26px 22px;
  }
  .private-badge {
    display: none;
  }
  .result-heading h2 {
    font-size: 20px;
  }
  .day-tabs button {
    padding: 10px 8px;
  }
  .promise-row {
    gap: 12px;
  }
  .replan-form {
    flex-wrap: wrap;
  }
}
@media (max-width: 760px) {
  .agent-workspace {
    inset: 0 0 68px;
  }
  .workspace-header {
    height: 78px;
    min-height: 78px;
    padding: 0 18px;
  }
  .workspace-heading {
    gap: 10px;
  }
  .workspace-heading h1 {
    font-size: 18px;
  }
  .workspace-heading .eyebrow {
    font-size: 8px;
  }
  .workspace-grid {
    grid-template-columns: 1fr;
  }
  .brief-column {
    padding: 27px 22px;
    border-right: 0;
    border-bottom: 1px solid #dcdccc;
  }
  .brief-intro {
    position: relative;
    padding-left: 58px;
  }
  .companion-seal {
    position: absolute;
    left: 0;
    top: 0;
  }
  .brief-intro h2 {
    font-size: 23px;
    white-space: normal;
    margin: 9px 0;
  }
  .brief-intro h2 br {
    display: none;
  }
  .brief-intro > p:last-child {
    font-size: 11px;
  }
  .brief-intro .eyebrow {
    font-size: 7px;
    letter-spacing: 0.7px;
  }
  .travel-brief {
    gap: 15px;
  }
  .field-pair {
    gap: 13px;
  }
  .result-column {
    padding: 27px 22px 35px;
  }
  .result-empty {
    min-height: 440px;
  }
  .empty-atlas {
    width: 160px;
    height: 160px;
    margin: 10px 0 20px;
  }
  .empty-atlas svg {
    width: 50px;
  }
  .result-empty h2 {
    font-size: 24px;
  }
  .workspace-header-actions .text-button {
    font-size: 10px;
  }
  .result-heading h2 {
    font-size: 20px;
  }
  .history-strip {
    margin: 15px 18px 0;
    padding: 14px;
  }
  .confirmation-card {
    padding: 16px;
  }
  .confirmation-card > div {
    flex-wrap: wrap;
  }
  .story-paper {
    padding: 20px;
  }
  .day-timeline > li {
    gap: 10px;
  }
  .day-timeline > li:not(:last-child):after {
    left: 64px;
  }
  .day-tabs {
    gap: 6px;
  }
  .day-tabs button {
    padding: 10px 7px;
  }
  .day-tabs strong {
    font-size: 12px;
  }
  .day-tabs small {
    font-size: 7px;
  }
  .day-tabs span {
    font-size: 8px;
  }
  .field input,
  .field select,
  .field textarea {
    font-size: 16px;
    min-height: 42px;
  }
  .candidate-input .field input {
    font-size: 14px;
  }
  .primary-action {
    min-height: 45px;
  }
  .text-button {
    min-height: 32px;
  }
}
</style>
