<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import {
  ArrowRight,
  BookOpen,
  Check,
  CircleAlert,
  Compass,
  History,
  KeyRound,
  LoaderCircle,
  MapPin,
  Palette,
  RefreshCw,
  Settings2,
  ShieldCheck,
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
  <main class="account-home" aria-label="我的旅行档案">
    <div class="account-scroll">
      <div class="account-page">
        <header class="account-hero">
          <div>
            <p class="journey-kicker">YOUR JOURNEY, ALL TOGETHER</p>
            <h1>把旅行，<em>慢慢收成自己的档案。</em></h1>
            <p>从一个想法，到一次抵达，再到值得重读的故事。</p>
          </div>
          <button
            class="journey-secondary"
            type="button"
            @click="emit('connect')"
          >
            <Settings2 :size="16" />{{
              hasSession ? '连接设置' : '连接我的档案'
            }}
          </button>
        </header>
        <section
          v-if="!connected"
          class="account-connect-state"
          :class="{ interrupted: hasSession }"
          aria-label="档案连接状态"
        >
          <span><KeyRound :size="27" /></span>
          <div>
            <h2>
              {{
                hasSession
                  ? '暂时无法读取你的档案'
                  : '先熟悉旅程，再连接私人档案。'
              }}
            </h2>
            <p>
              {{
                hasSession
                  ? '当前数据尚未读取成功。可以重新读取，或检查本页的连接令牌。'
                  : '公开发现页可以直接浏览。连接后，才能查看自己的行程、城市和旅行记忆。'
              }}
            </p>
          </div>
          <button
            v-if="hasSession"
            class="journey-primary"
            type="button"
            :disabled="refreshing"
            @click="emit('refresh')"
          >
            <RefreshCw :size="15" />重新读取档案</button
          ><button
            v-else
            class="journey-primary"
            type="button"
            @click="emit('connect')"
          >
            连接私人档案<ArrowRight :size="16" />
          </button>
        </section>
        <section v-else class="account-identity" aria-label="已读取的私人档案">
          <span class="account-avatar"><UserRound :size="28" /></span>
          <div>
            <span class="account-identity-kicker">YOUR PRIVATE ARCHIVE</span>
            <h2>{{ overview.username }}</h2>
            <p><ShieldCheck :size="13" />本页已连接 · 私人记录由你确认保存</p>
          </div>
          <dl>
            <div>
              <dt>城市</dt>
              <dd>{{ overview.stats.lit_cities }}</dd>
            </div>
            <div>
              <dt>记忆</dt>
              <dd>{{ overview.stats.memories }}</dd>
            </div>
            <div>
              <dt>照片</dt>
              <dd>{{ overview.stats.photos }}</dd>
            </div>
          </dl>
        </section>
        <section class="account-guide" aria-labelledby="account-guide-title">
          <div class="account-section-title">
            <div>
              <p class="journey-kicker">ONE STEP AT A TIME</p>
              <h2 id="account-guide-title">这一次，你想从哪里开始？</h2>
            </div>
            <span>选择一件事，跟着完成。</span>
          </div>
          <div class="account-guide-grid">
            <article v-for="(guide, index) in guides" :key="guide.view">
              <div class="account-guide-top">
                <span><component :is="guide.icon" :size="24" /></span
                ><small>0{{ index + 1 }}</small>
              </div>
              <h3>{{ guide.title }}</h3>
              <p>{{ guide.text }}</p>
              <button
                type="button"
                class="journey-text-action"
                @click="emit('select', guide.view)"
              >
                {{ guide.label }}<ArrowRight :size="15" />
              </button>
            </article>
          </div>
        </section>
        <section v-if="connected" class="account-lower">
          <article class="account-recent" aria-labelledby="recent-title">
            <div class="account-section-title">
              <div>
                <p class="journey-kicker">PICK UP YOUR LAST CHAPTER</p>
                <h2 id="recent-title">接着上次的旅程</h2>
              </div>
              <button
                class="account-refresh"
                type="button"
                aria-label="刷新档案任务与能力"
                :disabled="loading"
                @click="loadResources"
              >
                <RefreshCw :size="16" :class="{ spin: loading }" />
              </button>
            </div>
            <p v-if="loading" class="account-list-state" role="status">
              <LoaderCircle class="spin" :size="19" />正在读取最近任务
            </p>
            <div
              v-else-if="historyError"
              class="account-list-state error"
              role="alert"
            >
              <CircleAlert :size="20" />
              <p>{{ historyError }}</p>
              <button
                type="button"
                class="journey-text-action"
                @click="loadResources"
              >
                重新读取任务
              </button>
            </div>
            <div v-else-if="!runs.length" class="account-no-tasks">
              <History :size="30" />
              <h3>第一段旅程，等你开始。</h3>
              <p>规划与故事任务会留在这里，随时可以接着查看。</p>
              <button
                type="button"
                class="journey-text-action"
                @click="emit('select', 'journeys')"
              >
                去规划一段旅行<ArrowRight :size="15" />
              </button>
            </div>
            <div v-else class="account-task-list">
              <button
                v-for="run in runs.slice(0, 4)"
                :key="run.id"
                type="button"
                :aria-label="`打开${run.kind === 'plan' ? '行程' : '故事'}：${run.title}`"
                @click="emit('openRun', run)"
              >
                <span class="account-task-icon"
                  ><Compass v-if="run.kind === 'plan'" :size="19" /><BookOpen
                    v-else
                    :size="19" /></span
                ><span class="account-task-copy"
                  ><strong>{{ run.title }}</strong
                  ><small
                    >{{ run.kind === 'plan' ? '行程' : '故事' }} · 第{{
                      run.revision
                    }}版 · {{ date(run.updated_at) }}</small
                  ></span
                ><span class="account-task-status" :class="run.status">{{
                  statusLabels[run.status]
                }}</span
                ><ArrowRight :size="15" />
              </button>
            </div>
            <p class="account-history-note">
              打开任务只读取原记录，不会重新生成或自动确认保存。
            </p>
          </article>
          <aside
            class="account-capabilities"
            aria-labelledby="capability-title"
          >
            <div class="account-section-title">
              <div>
                <p class="journey-kicker">WHAT YOU CAN DO TODAY</p>
                <h2 id="capability-title">当前可用能力</h2>
              </div>
              <ShieldCheck :size="19" />
            </div>
            <ul>
              <li v-for="service in services" :key="service.name">
                <component :is="service.icon" :size="18" />
                <div>
                  <strong>{{ service.name }}</strong>
                  <p>{{ service.text }}</p>
                </div>
                <span :class="{ ready: service.ready }"
                  ><Check v-if="service.ready" :size="12" />{{
                    service.state
                  }}</span
                >
              </li>
            </ul>
            <p class="account-service-note">
              配置状态来自当前服务。在线查询或生成是否成功，以实际任务结果为准。
            </p>
            <button
              type="button"
              class="journey-text-action"
              @click="emit('select', 'studio')"
            >
              看看影像创作空间<ArrowRight :size="15" />
            </button>
          </aside>
        </section>
        <footer class="account-footer">
          <ShieldCheck :size="15" />
          <p>
            先预览，再确认。私人读取、可能收费的调用和保存操作，由你分别决定。
          </p>
        </footer>
      </div>
    </div>
  </main>
</template>

<style scoped>
.account-home {
  position: absolute;
  inset: var(--product-header-height) 0 var(--product-bottom-height);
  overflow: hidden;
  background: var(--page-bg);
  color: #40513a;
}
.account-scroll {
  height: 100%;
  overflow: auto;
  scrollbar-gutter: stable;
}
.account-page {
  width: min(1280px, calc(100% - 80px));
  margin: auto;
  padding: 38px 0 30px;
}
.account-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 25px;
  margin-bottom: 28px;
}
.account-hero h1 {
  font-size: clamp(27px, 2.5vw, 34px);
  font-weight: 550;
  letter-spacing: -1px;
  line-height: 1.5;
  margin: 0;
}
.account-hero h1 em {
  font-style: normal;
  color: #b25936;
  font-weight: inherit;
}
.account-hero > div > p:last-child {
  color: #6e7c62;
  font-size: 13px;
  line-height: 1.9;
  margin: 11px 0 0;
}
.account-hero > button {
  flex: none;
}
.account-connect-state {
  display: flex;
  align-items: center;
  gap: 21px;
  padding: 26px;
  border: 1px solid #e6dcc9;
  border-radius: 12px;
  background: #fbf5e8;
  margin-bottom: 31px;
}
.account-connect-state > span,
.account-avatar {
  display: grid;
  place-items: center;
  flex: none;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  color: #b28c58;
  background: #f1e6cd;
}
.account-connect-state > div {
  flex: 1;
  min-width: 0;
}
.account-connect-state h2 {
  margin: 0 0 9px;
  font-size: 19px;
  font-weight: 500;
}
.account-connect-state p {
  margin: 0;
  max-width: 650px;
  color: #7b7b60;
  font-size: 12px;
  line-height: 1.9;
}
.account-identity {
  display: flex;
  align-items: center;
  gap: 22px;
  padding: 27px 30px;
  border: 1px solid #e6e3d3;
  border-radius: 12px;
  background: #fffdf7;
  margin-bottom: 32px;
}
.account-avatar {
  width: 64px;
  height: 64px;
  color: #9a9d73;
  background: #f0f0df;
}
.account-identity-kicker {
  color: #897e62;
  font-size: 8px;
  letter-spacing: 1.5px;
}
.account-identity h2 {
  font-size: 23px;
  line-height: 1.5;
  font-weight: 500;
  margin: 6px 0 8px;
  overflow-wrap: anywhere;
}
.account-identity p {
  display: flex;
  gap: 6px;
  align-items: center;
  margin: 0;
  font-size: 10px;
  color: #6e7d5d;
}
.account-identity dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  min-width: 330px;
  gap: 0;
  margin: 0 0 0 auto;
}
.account-identity dl > div {
  display: flex;
  flex-direction: column-reverse;
  gap: 8px;
  text-align: center;
  padding: 0 24px;
  border-left: 1px solid #e9e4d6;
}
.account-identity dt {
  color: #727d61;
  font-size: 11px;
}
.account-identity dd {
  margin: 0;
  color: #495c3c;
  font-family: Georgia, serif;
  font-size: 31px;
  line-height: 1.2;
}
.account-section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
  margin-bottom: 19px;
}
.account-section-title h2 {
  margin: 0;
  color: #526344;
  font-size: 20px;
  line-height: 1.5;
  font-weight: 550;
}
.account-section-title .journey-kicker {
  font-size: 8px;
  color: #8a805f;
  margin-bottom: 7px;
}
.account-section-title > span {
  color: #788469;
  font-size: 11px;
}
.account-guide-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 19px;
}
.account-guide-grid article {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding: 24px;
  border: 1px solid #e2e5d6;
  border-radius: 11px;
  background: #fffef8;
}
.account-guide-grid article:nth-child(2) {
  background: #f6f8ee;
}
.account-guide-grid article:nth-child(3) {
  background: #fbf6ec;
}
.account-guide-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
}
.account-guide-top > span {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border: 1px solid #e8dcc0;
  border-radius: 11px;
  color: #ad8952;
  background: #fcf3de;
}
.account-guide-top > small {
  color: #8d8162;
  font-family: Georgia, serif;
  font-size: 18px;
}
.account-guide-grid h3 {
  margin: 0 0 12px;
  font-size: 18px;
  font-weight: 500;
  color: #5d6f4d;
}
.account-guide-grid p {
  margin: 0 0 16px;
  font-size: 12px;
  line-height: 1.95;
  color: #728262;
  flex: 1;
}
.account-guide-grid button {
  align-self: flex-start;
  font-size: 12px;
}
.account-lower {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
  gap: 23px;
  margin-top: 31px;
  align-items: start;
}
.account-recent,
.account-capabilities {
  min-width: 0;
  padding: 24px;
  border: 1px solid #e4e5d6;
  border-radius: 11px;
  background: #fffdf7;
}
.account-refresh {
  display: grid;
  place-items: center;
  width: 35px;
  height: 35px;
  border: 1px solid #dde3cc;
  border-radius: 6px;
  background: #fafbf0;
  color: #70805c;
  cursor: pointer;
}
.account-refresh:disabled {
  opacity: 0.5;
  cursor: wait;
}
.account-task-list > button {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 17px 0;
  border: 0;
  border-top: 1px solid #eceadd;
  background: transparent;
  color: #687c53;
  text-align: left;
  cursor: pointer;
}
.account-task-list > button:hover {
  color: #b15935;
}
.account-task-icon {
  display: grid;
  place-items: center;
  flex: none;
  width: 38px;
  height: 42px;
  background: #f4efdf;
  border-radius: 7px;
  color: #a38250;
}
.account-task-copy {
  display: flex;
  flex-direction: column;
  gap: 7px;
  flex: 1;
  min-width: 0;
}
.account-task-copy strong {
  font-size: 13px;
  line-height: 1.6;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.account-task-copy small {
  color: #748263;
  font-size: 10px;
  line-height: 1.7;
}
.account-task-status {
  flex: none;
  padding: 4px 7px;
  border: 1px solid #e5d9bd;
  border-radius: 5px;
  color: #8b7249;
  background: #fcf6e7;
  font-size: 9px;
  white-space: nowrap;
}
.account-task-status.confirmed {
  color: #607c42;
  background: #f0f6e6;
  border-color: #d6e2c2;
}
.account-task-status.failed {
  color: #a6583d;
  background: #fff1e6;
  border-color: #e5c5ae;
}
.account-history-note,
.account-service-note {
  margin: 13px 0 0;
  padding-top: 13px;
  border-top: 1px solid #e7e7d8;
  color: #6e7d5f;
  font-size: 10px;
  line-height: 1.9;
}
.account-capabilities > .account-section-title > svg {
  color: #86966f;
}
.account-capabilities ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.account-capabilities li {
  display: flex;
  align-items: flex-start;
  gap: 11px;
  padding: 16px 0;
  border-top: 1px solid #ecebdd;
}
.account-capabilities li > svg {
  flex: none;
  color: #9a8d63;
  margin-top: 3px;
}
.account-capabilities li > div {
  flex: 1;
  min-width: 0;
}
.account-capabilities li strong {
  font-size: 12px;
  font-weight: 500;
  color: #62764e;
}
.account-capabilities li p {
  font-size: 10px;
  line-height: 1.8;
  color: #70825e;
  margin: 6px 0 0;
}
.account-capabilities li > span {
  display: flex;
  align-items: center;
  gap: 3px;
  flex: none;
  padding: 4px 6px;
  border-radius: 5px;
  color: #8a744c;
  background: #fbf3e1;
  font-size: 9px;
}
.account-capabilities li > span.ready {
  color: #648247;
  background: #eef4e2;
}
.account-capabilities > .journey-text-action {
  font-size: 11px;
  margin-top: 10px;
}
.account-no-tasks,
.account-list-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 195px;
  gap: 14px;
  padding: 15px;
  text-align: center;
  color: #8f946c;
}
.account-no-tasks h3 {
  font-size: 17px;
  font-weight: 500;
  margin: 0;
  color: #64794d;
}
.account-no-tasks p {
  color: #728361;
  font-size: 12px;
  margin: 0;
  line-height: 1.8;
}
.account-list-state {
  font-size: 12px;
  line-height: 1.9;
}
.account-list-state.error {
  color: #a5663c;
}
.account-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin-top: 28px;
  padding-top: 21px;
  border-top: 1px solid #e6e6d7;
  color: #6f805b;
}
.account-footer p {
  margin: 0;
  font-size: 10px;
  line-height: 1.8;
}
@media (max-width: 1100px) {
  .account-page {
    width: calc(100% - 48px);
  }
  .account-identity dl {
    min-width: 260px;
  }
  .account-identity dl > div {
    padding: 0 19px;
  }
  .account-guide-grid {
    gap: 14px;
  }
  .account-guide-grid article {
    padding: 21px;
  }
  .account-lower {
    grid-template-columns: minmax(0, 1fr);
  }
}
@media (max-width: 899px) {
  .account-hero {
    align-items: flex-start;
  }
  .account-hero h1 {
    font-size: 28px;
  }
  .account-hero h1 em {
    display: block;
  }
  .account-hero > button {
    font-size: 11px;
    margin-top: 20px;
  }
  .account-connect-state {
    flex-wrap: wrap;
    padding: 23px;
    gap: 17px;
  }
  .account-connect-state > div {
    min-width: 60%;
  }
  .account-connect-state > button {
    margin-left: 77px;
  }
  .account-identity {
    gap: 17px;
    padding: 24px;
  }
  .account-identity dl {
    min-width: 225px;
  }
  .account-identity dl > div {
    padding: 0 15px;
  }
  .account-identity h2 {
    font-size: 21px;
  }
  .account-guide-grid {
    grid-template-columns: minmax(0, 1fr);
  }
  .account-guide-grid article {
    position: relative;
    padding: 22px 24px 22px 95px;
    min-height: 180px;
  }
  .account-guide-top {
    position: absolute;
    left: 24px;
    top: 23px;
    flex-direction: column;
    gap: 16px;
    margin: 0;
  }
  .account-guide-top small {
    font-size: 14px;
  }
  .account-guide-grid h3 {
    font-size: 18px;
  }
  .account-guide-grid p {
    max-width: 490px;
  }
  .account-section-title > span {
    display: none;
  }
}
@media (max-width: 580px) {
  .account-page {
    width: calc(100% - 32px);
    padding-top: 24px;
  }
  .account-hero {
    flex-direction: column;
    gap: 17px;
    margin-bottom: 22px;
  }
  .account-hero h1 {
    font-size: 26px;
    line-height: 1.6;
  }
  .account-hero > div > p:last-child {
    font-size: 11px;
  }
  .account-hero > button {
    margin: 0;
    min-height: 39px;
  }
  .account-connect-state {
    padding: 19px;
    gap: 14px;
  }
  .account-connect-state > span {
    width: 43px;
    height: 43px;
  }
  .account-connect-state > div {
    min-width: 0;
    flex: 1;
  }
  .account-connect-state h2 {
    font-size: 16px;
    line-height: 1.7;
  }
  .account-connect-state p {
    font-size: 11px;
  }
  .account-connect-state > button {
    margin-left: 0;
    font-size: 11px;
  }
  .account-identity {
    flex-wrap: wrap;
    padding: 21px 19px;
    gap: 14px;
  }
  .account-avatar {
    width: 47px;
    height: 47px;
  }
  .account-identity > div {
    flex: 1;
    min-width: 0;
  }
  .account-identity h2 {
    font-size: 20px;
  }
  .account-identity p {
    font-size: 9px;
    line-height: 1.8;
  }
  .account-identity-kicker {
    font-size: 7px;
    letter-spacing: 1px;
  }
  .account-identity dl {
    width: 100%;
    min-width: 0;
    margin: 8px 0 0;
    padding-top: 19px;
    border-top: 1px solid #e7e4d5;
  }
  .account-identity dl > div {
    border-left: 0;
    border-right: 1px solid #e7e4d5;
  }
  .account-identity dl > div:last-child {
    border-right: 0;
  }
  .account-identity dd {
    font-size: 28px;
  }
  .account-section-title h2 {
    font-size: 18px;
  }
  .account-guide-grid article {
    padding: 22px 19px 21px 79px;
  }
  .account-guide-top {
    left: 19px;
    top: 21px;
  }
  .account-guide-top > span {
    width: 40px;
    height: 40px;
  }
  .account-guide-grid h3 {
    font-size: 17px;
  }
  .account-guide-grid p {
    font-size: 11px;
  }
  .account-guide-grid button {
    font-size: 11px;
  }
  .account-lower {
    margin-top: 24px;
    gap: 18px;
  }
  .account-recent,
  .account-capabilities {
    padding: 21px 17px;
  }
  .account-task-list > button {
    gap: 8px;
  }
  .account-task-copy strong {
    font-size: 12px;
  }
  .account-task-copy small {
    font-size: 9px;
  }
  .account-task-icon {
    width: 31px;
    height: 37px;
  }
  .account-task-status {
    font-size: 8px;
    padding: 4px 5px;
  }
  .account-task-list > button > svg {
    display: none;
  }
  .account-capabilities li {
    gap: 8px;
  }
  .account-capabilities li p {
    font-size: 10px;
  }
  .account-capabilities li > span {
    font-size: 8px;
    max-width: 101px;
    text-align: center;
  }
  .account-footer {
    align-items: flex-start;
    padding: 19px 6px 0;
  }
  .account-footer > svg {
    flex: none;
    margin-top: 2px;
  }
  .account-footer p {
    font-size: 9px;
  }
}
</style>
