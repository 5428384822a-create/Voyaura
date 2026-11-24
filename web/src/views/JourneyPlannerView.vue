<script setup lang="ts">
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  BusFront,
  CalendarDays,
  CarFront,
  Check,
  Clock3,
  ExternalLink,
  Footprints,
  LoaderCircle,
  MapPin,
  Plane,
  Route,
  Search,
  Sparkles,
  TrainFront,
} from 'lucide-vue-next'
import { computed, onMounted, ref, watch } from 'vue'
import {
  ApiClientError,
  getRouteCapabilities,
  getXiaoxiPlanningCapability,
  planLocalRoute,
  previewXiaoxiPlanning,
} from '../api'
import type {
  AppErrorInfo,
  LocalRouteMode,
  LocalRouteResult,
  MapOverview,
  RouteCapabilities,
  RouteProviderCapability,
  XiaoxiPlanningCapability,
  XiaoxiPlanningPreview,
  XiaoxiSearchCategory,
} from '../types'

const props = defineProps<{ overview: MapOverview }>()
const emit = defineEmits<{ back: [] }>()

const activeDesk = ref<'planning' | 'routes'>('planning')
const planningCapability = ref<XiaoxiPlanningCapability | null>(null)
const planningCapabilityError = ref<AppErrorInfo | null>(null)
const planningMessage = ref('')
const planningPhase = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const planningPreview = ref<XiaoxiPlanningPreview | null>(null)
const planningError = ref<AppErrorInfo | null>(null)

const capabilities = ref<RouteCapabilities | null>(null)
const capabilityError = ref<AppErrorInfo | null>(null)
const originAdcode = ref('')
const destinationAdcode = ref('')
const routeMode = ref<LocalRouteMode>('driving')
const routePhase = ref<'idle' | 'loading' | 'ready' | 'error'>('idle')
const routeResult = ref<LocalRouteResult | null>(null)
const routeError = ref<AppErrorInfo | null>(null)

const planningExamples = [
  '杭州三天，独自摄影，节奏轻松，公共交通为主',
  '广州两天，想吃本地菜，也想逛历史街区',
  '带父母去西安四天，少走路，午间要休息',
]
const localModes: Array<{ mode: LocalRouteMode; label: string; icon: typeof CarFront }> = [
  { mode: 'walking', label: '步行', icon: Footprints },
  { mode: 'transit', label: '公交地铁', icon: BusFront },
  { mode: 'driving', label: '驾车', icon: CarFront },
]
const categoryLabels: Record<XiaoxiSearchCategory, string> = {
  culture_history: '历史文化',
  museum_art: '博物馆与艺术',
  nature_scenery: '自然风景',
  photography: '摄影',
  family: '亲子',
  food: '美食',
  shopping: '购物',
  nightlife: '夜游',
  neighborhood: '街区',
  other: '其他',
}

const selectedOrigin = computed(() => (
  props.overview.visited_cities.find(city => city.adcode === originAdcode.value) ?? null
))
const selectedDestination = computed(() => (
  props.overview.visited_cities.find(city => city.adcode === destinationAdcode.value) ?? null
))
const canPlanRoute = computed(() => (
  selectedOrigin.value !== null
  && selectedDestination.value !== null
  && originAdcode.value !== destinationAdcode.value
  && routePhase.value !== 'loading'
))
const canAnalyze = computed(() => (
  planningMessage.value.trim().length > 0 && planningPhase.value !== 'loading'
))
const bestRoute = computed(() => routeResult.value?.options[0] ?? null)
const dailySlots = computed(() => Array.from(
  { length: planningPreview.value?.requirements.day_count ?? 0 },
  (_, index) => index + 1,
))
const planningStatusLabel = computed(() => {
  if (planningPhase.value === 'loading') return '正在分析'
  if (planningPreview.value?.status === 'ready_for_poi_search') return '需求草案'
  if (planningPreview.value?.status === 'needs_clarification') return '等待补充'
  return planningCapability.value?.available ? 'DeepSeek 就绪' : '需要配置模型'
})

watch(
  () => props.overview.visited_cities.map(city => city.adcode),
  () => {
    const cities = props.overview.visited_cities
    if (!cities.some(city => city.adcode === originAdcode.value)) {
      originAdcode.value = cities[0]?.adcode ?? ''
    }
    if (!cities.some(city => city.adcode === destinationAdcode.value)) {
      destinationAdcode.value = cities[1]?.adcode ?? cities[0]?.adcode ?? ''
    }
  },
  { immediate: true },
)

onMounted(async () => {
  const [routeCapabilityResult, planningCapabilityResult] = await Promise.allSettled([
    getRouteCapabilities(),
    getXiaoxiPlanningCapability(),
  ])
  if (routeCapabilityResult.status === 'fulfilled') {
    capabilities.value = routeCapabilityResult.value
  } else {
    capabilityError.value = normalizeError(routeCapabilityResult.reason)
  }
  if (planningCapabilityResult.status === 'fulfilled') {
    planningCapability.value = planningCapabilityResult.value
  } else {
    planningCapabilityError.value = normalizeError(planningCapabilityResult.reason)
  }
})

function normalizeError(error: unknown): AppErrorInfo {
  if (error instanceof ApiClientError) return error
  return {
    code: 'UNKNOWN_CLIENT_ERROR',
    message: '行程服务出现未知错误。',
    details: {},
    retryable: false,
  }
}

async function analyzePlanningRequest() {
  if (!canAnalyze.value) return
  planningPhase.value = 'loading'
  planningPreview.value = null
  planningError.value = null
  try {
    planningPreview.value = await previewXiaoxiPlanning({
      username: 'AuroraRovella',
      message: planningMessage.value.trim(),
    })
    planningPhase.value = 'ready'
  } catch (error) {
    planningError.value = normalizeError(error)
    planningPhase.value = 'error'
  }
}

async function submitRoute() {
  const origin = selectedOrigin.value
  const destination = selectedDestination.value
  if (!origin || !destination || !canPlanRoute.value) return
  routePhase.value = 'loading'
  routeResult.value = null
  routeError.value = null
  try {
    routeResult.value = await planLocalRoute({
      mode: routeMode.value,
      origin: { longitude: origin.longitude, latitude: origin.latitude },
      destination: { longitude: destination.longitude, latitude: destination.latitude },
      origin_adcode: origin.adcode,
      destination_adcode: destination.adcode,
    })
    routePhase.value = 'ready'
  } catch (error) {
    routeError.value = normalizeError(error)
    routePhase.value = 'error'
  }
}

function swapCities() {
  const currentOrigin = originAdcode.value
  originAdcode.value = destinationAdcode.value
  destinationAdcode.value = currentOrigin
  routePhase.value = 'idle'
  routeResult.value = null
}

function formatDuration(seconds: number) {
  const minutes = Math.max(1, Math.round(seconds / 60))
  if (minutes < 60) return `${minutes} 分钟`
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return rest ? `${hours} 小时 ${rest} 分钟` : `${hours} 小时`
}

function formatDistance(meters: number) {
  return meters < 1000 ? `${meters} 米` : `${(meters / 1000).toFixed(1)} 公里`
}

function intercityLabel(mode: RouteProviderCapability['mode']) {
  const labels: Partial<Record<RouteProviderCapability['mode'], string>> = {
    high_speed_rail: '高铁 / 动车',
    train: '普通火车',
    flight: '飞机',
  }
  return labels[mode] ?? mode
}

function intercityIcon(mode: RouteProviderCapability['mode']) {
  return mode === 'flight' ? Plane : TrainFront
}

function providerLabel(provider: string) {
  return {
    licensed_rail_partner: '正式铁路合作方',
    amadeus_or_china_licensed_partner: 'Amadeus / 国内授权源',
  }[provider] ?? provider
}

function dataFieldLabel(field: string) {
  return {
    train_number: '车次',
    flight_number: '航班号',
    schedule: '时刻',
    seat_class: '席别',
    price: '价格',
    fare: '票价',
    cabin: '舱位',
    availability: '余量',
  }[field] ?? field
}
</script>

<template>
  <main class="journey-planner-view">
    <header class="journey-planner-header">
      <button type="button" title="返回地图" aria-label="返回地图" @click="emit('back')"><ArrowLeft :size="20" /></button>
      <div><h1>行程路线</h1></div>
      <span><Route :size="17" />GCJ-02</span>
    </header>

    <nav class="journey-desk-tabs" aria-label="行程工作台" role="tablist">
      <button type="button" role="tab" :aria-selected="activeDesk === 'planning'" :class="{ active: activeDesk === 'planning' }" @click="activeDesk = 'planning'"><Sparkles :size="16" />智能规划</button>
      <button type="button" role="tab" :aria-selected="activeDesk === 'routes'" :class="{ active: activeDesk === 'routes' }" @click="activeDesk = 'routes'"><Route :size="16" />路线工具</button>
    </nav>

    <div class="journey-planner-scroll">
      <section class="route-query-band" aria-labelledby="local-route-title">
        <div class="route-section-heading">
          <div><h2 id="local-route-title">市内与接驳路线</h2></div>
          <small>高德 · 实时查询</small>
        </div>

            <div class="planning-flow" aria-label="规划阶段">
              <div :class="{ complete: planningPreview }"><span><Check v-if="planningPreview" :size="15" /><Sparkles v-else :size="15" /></span><div><small>01</small><strong>需求草案</strong></div></div>
              <div><span><Search :size="15" /></span><div><small>02</small><strong>高德核验</strong></div></div>
              <div><span><MapPin :size="15" /></span><div><small>03</small><strong>每日区域</strong></div></div>
              <div><span><CalendarDays :size="15" /></span><div><small>04</small><strong>时间线</strong></div></div>
            </div>
          </div>
        </section>

        <section v-if="planningPreview" class="planning-result-band" aria-live="polite">
          <div class="planning-result-header">
            <div><p class="eyebrow">REQUIREMENT DRAFT</p><h2>{{ planningPreview.requirements.city_name ?? '等待确认城市' }}<template v-if="planningPreview.requirements.day_count"> · {{ planningPreview.requirements.day_count }} 天</template></h2></div>
            <span>{{ planningPreview.status === 'ready_for_poi_search' ? '待高德核验' : '等待补充' }}</span>
          </div>

      <section class="intercity-band" aria-labelledby="intercity-title">
        <div class="route-section-heading"><div><h2 id="intercity-title">跨城铁路与航班</h2></div><small>班次 · 票价 · 余量</small></div>
        <div v-if="capabilityError" class="route-inline-error"><AlertTriangle :size="17" /><span>{{ capabilityError.message }} · {{ capabilityError.code }}</span></div>
        <div v-else-if="!capabilities" class="intercity-loading"><LoaderCircle class="spin" :size="22" />正在读取 Provider</div>
        <div v-else class="intercity-grid">
          <article v-for="item in capabilities.intercity" :key="item.mode">
            <span class="intercity-icon"><component :is="intercityIcon(item.mode)" :size="23" /></span>
            <div><small>{{ providerLabel(item.provider) }}</small><h3>{{ intercityLabel(item.mode) }}</h3></div>
            <span class="provider-state">待合作方授权</span>
            <p>{{ item.notice }}</p>
            <div class="provider-fields"><span v-for="field in item.data_scope" :key="field">{{ dataFieldLabel(field) }}</span></div>
            <a v-if="item.application_url" :href="item.application_url" target="_blank" rel="noreferrer">申请接口<ExternalLink :size="14" /></a>
          </article>
        </div>
      </section>
    </div>
  </main>
</template>
