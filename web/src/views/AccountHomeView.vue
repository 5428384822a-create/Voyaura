<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import {
  ArrowRight,
  BookOpen,
  CircleAlert,
  Compass,
  History,
  KeyRound,
  LoaderCircle,
  MapPin,
  Palette,
  RefreshCw,
  Settings2,
  Sparkles,
  UserRound,
} from 'lucide-vue-next'
import {
  getAgentCapabilities,
  listAgentRuns,
  type AgentCapabilities,
  type AgentRun,
} from '../api/agent'
import { getImageStyles } from '../api/client'
import UiButton from '../components/UiButton.vue'
import UiStatus from '../components/UiStatus.vue'
import type { AppView, ImageStyleCatalog, MapOverview } from '../types'

const props = defineProps<{
  overview: MapOverview
  connected: boolean
  hasSession: boolean
  refreshing?: boolean
}>()
const emit = defineEmits<{
  connect: []
  refresh: []
  select: [view: AppView]
  openRun: [run: AgentRun]
}>()
const capabilities = ref<AgentCapabilities | null>(null)
const catalog = ref<ImageStyleCatalog | null>(null)
const runs = ref<AgentRun[]>([])
const loading = ref(false)
const historyError = ref('')
const capabilityError = ref(false)
const imageStatusError = ref(false)
let version = 0
let disposed = false
const statusLabels: Record<AgentRun['status'], string> = {
  running: '执行中',
  needs_input: '待补充',
  awaiting_confirmation: '待核对草案',
  confirmed: '已保存',
  failed: '未完成',
}
const guides: Array<{
  view: AppView
  title: string
  text: string
  icon: typeof Compass
  label: string
}> = [
  {
    view: 'journeys',
    title: '安排下一段旅程',
    text: '告诉小曦目的地和节奏；没有在线地点时，可先填入离线演练条件。',
    icon: Compass,
    label: '去规划行程',
  },
  {
    view: 'map',
    title: '留下抵达与记忆',
    text: '手动选择去过的城市，预览确认后，再写下日期、文字与心情。',
    icon: MapPin,
    label: '去记录旅程',
  },
  {
    view: 'memories',
    title: '把回忆连成故事',
    text: '从已有记录出发，选择城市和日期，授权整理，编辑并确认保存。',
    icon: BookOpen,
    label: '去翻阅记忆',
  },
]
const services = computed(() => [
  {
    name: '本地规划与故事',
    icon: BookOpen,
    state: capabilities.value
      ? '可使用'
      : capabilityError.value
        ? '暂无法确认'
        : '读取中',
    ready: !!capabilities.value,
    text: '依据已提供的地点与授权记录整理。',
  },
  {
    name: '在线地点查询',
    icon: MapPin,
    state: capabilities.value
      ? capabilities.value.amap_configured
        ? '已配置 · 需授权'
        : '尚未连接'
      : '状态待确认',
    ready: !!capabilities.value?.amap_configured,
    text: '未连接时，可补充自己的地点或使用演练。',
  },
  {
    name: '模型辅助理解',
    icon: Sparkles,
    state: capabilities.value
      ? capabilities.value.model_configured
        ? '已配置 · 需授权'
        : '尚未连接'
      : '状态待确认',
    ready: !!capabilities.value?.model_configured,
    text: '启用前单独授权，可能产生调用费用。',
  },
  {
    name: '照片风格创作',
    icon: Palette,
    state: catalog.value
      ? catalog.value.available
        ? '已配置 · 需确认'
        : '尚未连接'
      : imageStatusError.value
        ? '暂无法确认'
        : '读取中',
    ready: !!catalog.value?.available,
    text: '从自己的可用照片发起，原片与来源保留。',
  },
])
async function loadResources() {
  const current = ++version
  if (!props.connected) {
    capabilities.value = null
    catalog.value = null
    runs.value = []
    loading.value = false
    return
  }
  loading.value = true
  historyError.value = ''
  const results = await Promise.allSettled([
    getAgentCapabilities(),
    getImageStyles(),
    listAgentRuns(),
  ])
  if (disposed || current !== version) return
  if (results[0].status === 'fulfilled') {
    capabilities.value = results[0].value
    capabilityError.value = false
  } else {
    capabilities.value = null
    capabilityError.value = true
  }
  if (results[1].status === 'fulfilled') {
    catalog.value = results[1].value
    imageStatusError.value = false
  } else {
    catalog.value = null
    imageStatusError.value = true
  }
  if (results[2].status === 'fulfilled') runs.value = results[2].value.items
  else
    historyError.value =
      results[2].reason instanceof Error
        ? results[2].reason.message
        : '最近任务暂时无法读取。'
  loading.value = false
}
watch(
  () => props.connected,
  () => void loadResources(),
  { immediate: true },
)
onBeforeUnmount(() => {
  disposed = true
  version += 1
})
function date(value: string) {
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime())
    ? '日期待确认'
    : new Intl.DateTimeFormat('zh-CN', {
        month: 'short',
        day: 'numeric',
      }).format(parsed)
}
</script>

<template>
  <main class="account-home" aria-label="我的旅行档案"><div class="account-scroll"><div class="account-page">
    <header class="account-hero"><div><h1>我的档案</h1><p>继续上次的旅程，或者记录新的抵达。</p></div><UiButton v-if="hasSession" variant="tertiary" @click="emit('connect')"><Settings2 :size="18" />连接设置</UiButton></header>
    <section v-if="!connected" class="account-connect-state" :class="{ interrupted: hasSession }" aria-label="档案连接状态"><KeyRound :size="30" /><div><h2>{{ hasSession ? '暂时无法读取档案' : '连接你的旅行档案' }}</h2><p>{{ hasSession ? '重新读取，或在连接设置中检查访问令牌。' : '连接后查看自己的行程、城市与旅行记忆。发现页可以直接浏览。' }}</p></div><UiButton v-if="hasSession" variant="primary" :loading="refreshing" @click="emit('refresh')">重新读取档案</UiButton><UiButton v-else variant="primary" @click="emit('connect')">连接私人档案<ArrowRight :size="18" /></UiButton></section>
    <section v-else class="account-identity" aria-label="已读取的私人档案"><span class="account-avatar"><UserRound :size="26" /></span><div><h2>{{ overview.username }}</h2><UiStatus tone="success">已连接</UiStatus></div><dl><div><dt>城市</dt><dd>{{ overview.stats.lit_cities }}</dd></div><div><dt>记忆</dt><dd>{{ overview.stats.memories }}</dd></div><div><dt>照片</dt><dd>{{ overview.stats.photos }}</dd></div></dl></section>
    <section v-if="connected" class="account-recent" aria-labelledby="recent-title"><div class="account-section-title"><h2 id="recent-title">最近任务</h2><UiButton class="account-refresh" variant="tertiary" :disabled="loading" aria-label="刷新档案任务与能力" @click="loadResources"><RefreshCw :size="18" :class="{ spin: loading }" />刷新</UiButton></div>
      <p v-if="loading" class="account-list-state" role="status"><LoaderCircle class="spin" :size="20" />正在读取最近任务</p>
      <div v-else-if="historyError" class="account-list-state error" role="alert"><CircleAlert :size="22" /><p>{{ historyError }}</p><UiButton variant="secondary" @click="loadResources">重新读取任务</UiButton></div>
      <div v-else-if="!runs.length" class="account-no-tasks"><History :size="32" /><div><h3>还没有任务</h3><p>从一个旅行想法开始，之后可以在这里接着查看。</p></div><UiButton variant="primary" @click="emit('select','journeys')">规划一段旅行<ArrowRight :size="18" /></UiButton></div>
      <div v-else class="account-task-list"><button v-for="run in runs.slice(0,4)" :key="run.id" type="button" :aria-label="`打开${run.kind === 'plan' ? '行程' : '故事'}：${run.title}`" @click="emit('openRun',run)"><span class="account-task-icon"><Compass v-if="run.kind==='plan'" :size="22" /><BookOpen v-else :size="22" /></span><span class="account-task-copy"><strong>{{ run.title }}</strong><small>{{ run.kind==='plan'?'行程':'故事' }} · 第{{ run.revision }}版 · {{ date(run.updated_at) }}</small></span><UiStatus class="account-task-status" :class="run.status" :tone="run.status==='confirmed'?'success':run.status==='failed'?'error':run.status==='needs_input'?'warning':'neutral'">{{ statusLabels[run.status] }}</UiStatus><ArrowRight :size="18" /></button></div>
    </section>
    <nav class="account-shortcuts" aria-label="档案快捷操作"><UiButton v-for="guide in guides" :key="guide.view" variant="secondary" @click="emit('select',guide.view)"><component :is="guide.icon" :size="19" />{{ guide.label }}<ArrowRight :size="17" /></UiButton></nav>
    <details class="account-guide ui-disclosure" :open="!connected || (!loading && !runs.length && !historyError)"><summary>使用指南</summary><div class="account-guide-grid"><article v-for="guide in guides" :key="guide.view"><h3>{{ guide.title }}</h3><p>{{ guide.text }}</p></article></div></details>
    <details v-if="connected" class="account-capabilities ui-disclosure"><summary>服务状态</summary><ul><li v-for="service in services" :key="service.name"><component :is="service.icon" :size="20" /><div><strong>{{ service.name }}</strong><p>{{ service.text }}</p></div><UiStatus :tone="service.ready?'success':'neutral'">{{ service.state }}</UiStatus></li></ul><p class="account-service-note">这里显示配置状态，在线查询或生成以实际任务结果为准。</p><UiButton variant="tertiary" @click="emit('select','studio')">打开影像创作<ArrowRight :size="17" /></UiButton></details>
  </div></div></main>
</template>
<style scoped>
.account-home {
  position: absolute;
  inset: var(--product-header-height) 0 var(--product-bottom-height);
  overflow: hidden;
  background: var(--canvas);
  color: var(--text-body);
}
.account-scroll {
  height: 100%;
  overflow: auto;
  scrollbar-gutter: stable;
}
.account-page {
  width: min(1120px,calc(100% - 96px));
  margin: auto;
  padding: var(--space-7) 0;
}
.account-hero,
.account-section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-5);
}
.account-hero {
  margin-bottom: var(--space-6);
}
.account-hero h1 {
  margin: 0;
  font-size: var(--font-title);
  font-weight: 650;
  line-height: var(--line-heading);
  color: var(--text-primary);
}
.account-hero p {
  margin: 12px 0 0;
  font-size: var(--font-body);
  color: var(--text-secondary);
  line-height: var(--line-body);
}
.account-identity {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5) 0;
  border-block: 1px solid var(--border-subtle);
}
.account-avatar {
  display: grid;
  place-items: center;
  flex: none;
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: var(--surface-soft);
  color: var(--text-secondary);
}
.account-identity h2 {
  font-size: var(--font-card);
  font-weight: 550;
  margin: 0 0 8px;
  overflow-wrap: anywhere;
}
.account-identity dl {
  display: flex;
  gap: var(--space-7);
  margin: 0 0 0 auto;
}
.account-identity dl>div {
  display: flex;
  flex-direction: column-reverse;
  gap: 6px;
  min-width: 48px;
  text-align: center;
}
.account-identity dd {
  margin: 0;
  font-size: var(--font-title);
  font-weight: 550;
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
}
.account-identity dt {
  font-size: var(--font-secondary);
  color: var(--text-secondary);
}
.account-connect-state {
  display: flex;
  align-items: center;
  gap: var(--space-5);
  padding: var(--space-5);
  border-radius: var(--radius-surface);
  background: var(--surface-soft);
}
.account-connect-state>svg {
  flex: none;
  color: var(--action);
}
.account-connect-state>div {
  flex: 1;
  min-width: 0;
}
.account-connect-state h2 {
  margin: 0 0 8px;
  font-size: var(--font-section);
  font-weight: 550;
}
.account-connect-state p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--font-secondary);
  line-height: var(--line-body);
}
.account-recent {
  margin-top: var(--space-7);
}
.account-section-title {
  margin-bottom: var(--space-3);
}
.account-section-title h2 {
  margin: 0;
  font-size: var(--font-section);
  font-weight: 600;
  color: var(--text-primary);
}
.account-task-list {
  border-top: 1px solid var(--border-subtle);
}
.account-task-list>button {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  width: 100%;
  min-height: 90px;
  padding: 18px 4px;
  border: 0;
  border-bottom: 1px solid var(--border-subtle);
  background: transparent;
  color: var(--text-body);
  text-align: left;
  cursor: pointer;
}
.account-task-list>button:hover {
  background: var(--surface-soft);
}
.account-task-icon {
  display: grid;
  place-items: center;
  flex: none;
  width: 40px;
  height: 44px;
  color: var(--action);
}
.account-task-copy {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 0;
}
.account-task-copy strong {
  font-size: var(--font-body);
  font-weight: 550;
  line-height: 1.5;
  overflow-wrap: anywhere;
}
.account-task-copy small {
  font-size: var(--font-secondary);
  color: var(--text-secondary);
  line-height: 1.6;
}
.account-task-status {
  flex: none;
  max-width: 145px;
}
.account-task-list>button>svg {
  flex: none;
}
.account-shortcuts {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  margin-top: var(--space-6);
}
.account-guide-grid {
  display: grid;
  grid-template-columns: repeat(3,minmax(0,1fr));
  gap: var(--space-6);
  padding: var(--space-4) 0;
}
.account-guide-grid h3 {
  font-size: var(--font-card);
  font-weight: 550;
  margin: 0 0 10px;
}
.account-guide-grid p {
  font-size: var(--font-secondary);
  line-height: var(--line-body);
  color: var(--text-secondary);
  margin: 0;
}
.account-capabilities ul {
  list-style: none;
  padding: 0;
  margin: var(--space-3) 0;
}
.account-capabilities li {
  display: flex;
  gap: var(--space-3);
  align-items: flex-start;
  padding: var(--space-4) 0;
  border-bottom: 1px solid var(--border-subtle);
}
.account-capabilities li>svg {
  flex: none;
  color: var(--text-secondary);
  margin-top: 3px;
}
.account-capabilities li>div {
  flex: 1;
  min-width: 0;
}
.account-capabilities li strong {
  font-size: var(--font-body);
  font-weight: 550;
}
.account-capabilities li p {
  font-size: var(--font-secondary);
  color: var(--text-secondary);
  line-height: var(--line-body);
  margin: 6px 0 0;
}
.account-list-state,
.account-no-tasks {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-4);
  min-height: 155px;
  padding: var(--space-5);
  color: var(--text-secondary);
  font-size: var(--font-body);
  line-height: var(--line-body);
}
.account-list-state.error {
  color: var(--danger);
  flex-wrap: wrap;
}
.account-no-tasks h3 {
  font-size: var(--font-card);
  font-weight: 550;
  margin: 0 0 8px;
  color: var(--text-primary);
}
.account-no-tasks p {
  font-size: var(--font-secondary);
  margin: 0;
  line-height: var(--line-body);
}
@media(max-width:899px) {
  .account-page {
    width: calc(100% - 40px);
    padding-top: var(--space-6);
  }
  .account-identity dl {
    gap: var(--space-5);
  }
  .account-guide-grid {
    grid-template-columns: 1fr;
    gap: var(--space-5);
  }
  .account-hero {
    gap: var(--space-3);
  }
}
@media(max-width:580px) {
  .account-page {
    padding-top: var(--space-5);
  }
  .account-hero {
    align-items: flex-start;
    flex-wrap: wrap;
    margin-bottom: var(--space-5);
  }
  .account-hero p {
    font-size: var(--font-secondary);
  }
  .account-identity {
    flex-wrap: wrap;
  }
  .account-identity>div {
    flex: 1;
    min-width: 0;
  }
  .account-identity dl {
    justify-content: space-around;
    width: 100%;
    padding-top: var(--space-4);
    margin: 0;
    gap: var(--space-5);
  }
  .account-connect-state {
    align-items: flex-start;
    flex-wrap: wrap;
    padding: var(--space-5);
  }
  .account-connect-state>svg {
    display: none;
  }
  .account-connect-state h2 {
    font-size: var(--font-card);
  }
  .account-connect-state .ui-button {
    width: 100%;
  }
  .account-recent {
    margin-top: var(--space-6);
  }
  .account-task-list>button {
    display: grid;
    grid-template-columns: 24px minmax(0,1fr);
    gap: 8px 12px;
    padding: 18px 0;
  }
  .account-task-icon {
    grid-row: 1/3;
    width: 24px;
    align-self: start;
  }
  .account-task-copy {
    grid-column: 2;
  }
  .account-task-status {
    grid-column: 2;
    justify-self: start;
  }
  .account-task-list>button>svg {
    display: none;
  }
  .account-shortcuts {
    display: grid;
    grid-template-columns: 1fr;
  }
  .account-shortcuts .ui-button {
    justify-content: flex-start;
  }
  .account-shortcuts .ui-button>svg:last-child {
    margin-left: auto;
  }
  .account-no-tasks {
    align-items: flex-start;
    flex-wrap: wrap;
    justify-content: flex-start;
    padding: var(--space-5) 0;
  }
  .account-capabilities li {
    flex-wrap: wrap;
  }
  .account-capabilities li>.ui-status {
    margin-left: 32px;
  }
  .account-capabilities li>div {
    flex: 1 1 70%;
  }
}
@media(max-width:360px) {
  .account-page {
    width: calc(100% - 32px);
  }
}
</style>
