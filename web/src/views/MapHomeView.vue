<script setup lang="ts">
import {
  ArrowRight,
  BookOpen,
  CalendarDays,
  Camera,
  Compass,
  LoaderCircle,
  MapPin,
  Navigation,
  Plus,
  Search,
  Sparkles,
} from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import ChinaMapCanvas from '../components/ChinaMapCanvas.vue'
import type { MapOverview, VisitedCity } from '../types'

const props = defineProps<{
  overview: MapOverview
  apiConnected: boolean
  focusPoint: [number, number] | null
  checkInBusy: boolean
}>()
const emit = defineEmits<{
  openXiaoxi: []
  openStories: []
  manualCheckIn: []
  requestCheckIn: []
  searchPoi: []
  selectCity: [city: VisitedCity]
}>()

const selectedYear = ref<number | null>(null)
const query = ref('')
const selectedSummary = computed(() =>
  selectedYear.value === null
    ? null
    : (props.overview.year_summaries.find(
        (summary) => summary.year === selectedYear.value,
      ) ?? null),
)
const visibleOverview = computed<MapOverview>(() => {
  const summary = selectedSummary.value
  if (!summary) return props.overview
  const activities = new Map(summary.cities.map((city) => [city.adcode, city]))
  return {
    ...props.overview,
    stats: summary.stats,
    visited_cities: props.overview.visited_cities
      .filter((city) => activities.has(city.adcode))
      .map((city) => ({
        ...city,
        memory_count: activities.get(city.adcode)?.memory_count ?? 0,
      })),
  }
})

const visibleCities = computed(() => {
  const term = query.value.trim().toLocaleLowerCase()
  return visibleOverview.value.visited_cities.filter((city) =>
    `${city.name_zh} ${city.name_en} ${city.province_zh}`
      .toLocaleLowerCase()
      .includes(term),
  )
})

watch(
  () => props.overview.year_summaries.map((summary) => summary.year),
  (years) => {
    if (selectedYear.value !== null && !years.includes(selectedYear.value)) {
      selectedYear.value = null
    }
  },
)
</script>

<template>
  <main class="map-home journey-view" aria-label="我的旅行足迹">
    <div class="journey-scroll">
      <div class="journey-page">
        <header class="journey-hero">
          <div>

            <h1>走过的地方，<em>都有故事。</em></h1>
            <p>把一次次抵达，收进自己的旅行图鉴。</p>
          </div>
          <button
            class="journey-primary"
            type="button"
            :disabled="checkInBusy"
            @click="emit('manualCheckIn')"
          >
            <Plus :size="17" />记录一次抵达
          </button>
        </header>
        <nav class="journey-section-tabs" aria-label="旅程内容">
          <button class="active" type="button" aria-current="page">
            <Compass :size="17" />旅行足迹</button
          ><button type="button" @click="emit('openStories')">
            <BookOpen :size="17" />城市记忆
          </button>
        </nav>
        <section class="atlas-summary" aria-label="真实旅行统计">
          <div class="atlas-summary-label">
            <span class="atlas-sun"><Compass :size="25" /></span>
            <div><strong>{{
                selectedYear ? `${selectedYear} · 年度足迹` : '每一步，都算数。'
              }}</strong>
            </div>
          </div>
          <div class="stats-grid">
            <div>
              <strong>{{ visibleOverview.stats.lit_cities }}</strong
              ><span>点亮城市</span>
            </div>
            <div>
              <strong>{{ visibleOverview.stats.memories }}</strong
              ><span>旅行记忆</span>
            </div>
            <div>
              <strong>{{ visibleOverview.stats.photos }}</strong
              ><span>照片</span>
            </div>
            <div>
              <strong>{{ visibleOverview.stats.vlog_minutes }}</strong
              ><span>Vlog 分钟</span>
            </div>
          </div>
        </section>
        <div class="atlas-toolbar">
          <div>

            <h2 id="journey-summary-title">
              {{ selectedYear ? `${selectedYear} 年旅程` : '我的中国旅程' }}
            </h2>
          </div>
          <div class="atlas-year-filter">
            <CalendarDays :size="16" /><label class="sr-only" for="atlas-year"
              >按年份筛选旅行足迹</label
            ><select id="atlas-year" v-model="selectedYear">
              <option :value="null">全部年份</option>
              <option
                v-for="summary in overview.year_summaries"
                :key="summary.year"
                :value="summary.year"
              >
                {{ summary.year }} 年
              </option>
            </select>
          </div>
        </div>
        <div class="atlas-grid">
          <section class="atlas-map-stage" aria-label="地图与城市位置">
            <ChinaMapCanvas
              :overview="visibleOverview"
              :focus-point="focusPoint"
              @request-check-in="emit('requestCheckIn')"
              @select-city="emit('selectCity', $event)"
            />
            <div class="atlas-map-actions">
              <button
                class="journey-secondary"
                type="button"
                :disabled="checkInBusy"
                @click="emit('requestCheckIn')"
              >
                <LoaderCircle
                  v-if="checkInBusy"
                  class="spin"
                  :size="16"
                /><Navigation v-else :size="16" />{{
                  checkInBusy ? '正在定位' : '定位所在城市'
                }}</button
              ><button
                class="journey-secondary poi-search-entry"
                type="button"
                @click="emit('searchPoi')"
              >
                <Search :size="16" />搜地点
              </button>
            </div>
          </section>
          <aside class="atlas-city-list" aria-label="城市档案">
            <header>
              <div>

                <h2>收藏过的抵达</h2>
              </div>
              <span>{{ visibleOverview.visited_cities.length }}</span>
            </header>
            <label v-if="overview.visited_cities.length" class="archive-search"
              ><Search :size="17" /><input
                v-model="query"
                aria-label="查找已记录的城市"
                placeholder="查找城市或省份"
              /><button v-if="query" type="button" @click="query = ''">
                清空
              </button></label
            >
            <div v-if="visibleCities.length" class="atlas-city-items">
              <button
                v-for="city in visibleCities"
                :key="city.adcode"
                type="button"
                :aria-label="`打开${city.name_zh}的城市记忆`"
                @click="emit('selectCity', city)"
              >
                <span class="city-index-pin"><MapPin :size="19" /></span
                ><span
                  ><strong>{{ city.name_zh }}</strong
                  ><small
                    >{{ city.province_zh }} ·
                    {{ city.memory_count }} 段记忆</small
                  ></span
                ><ArrowRight :size="16" />
              </button>
            </div>
            <div v-else class="atlas-city-empty">
              <span><MapPin :size="28" /></span>
              <h3>
                {{
                  query
                    ? '没有找到这座城'
                    : selectedYear
                      ? '这一年还没有城市记录'
                      : '第一座城，等你写下。'
                }}
              </h3>
              <p>
                {{
                  query
                    ? '换个名称，或清空搜索看看。'
                    : '手动选择去过的城市，预览并确认后，再写下属于你的记忆。'
                }}
              </p>
              <button
                v-if="!query && !selectedYear"
                type="button"
                class="journey-text-action"
                @click="emit('manualCheckIn')"
              >
                记录一次抵达<ArrowRight :size="15" />
              </button>
            </div>
            <p class="atlas-private-note">
              <span class="status-dot" :class="{ online: apiConnected }"></span
              >{{ apiConnected ? '来自你的私人档案' : '档案连接待检查' }} ·
              计划不会自动点亮城市
            </p>
          </aside>
        </div>
        <section class="journey-next">
          <span class="journey-next-icon"><Camera :size="25" /></span>
          <div>

            <h2>抵达之后，把感受也留下。</h2>
            <p>写一段手记，添加自己的照片，再和小曦整理成旅行故事。</p>
          </div>
          <button
            class="journey-secondary"
            type="button"
            @click="emit('openStories')"
          >
            翻阅城市记忆<ArrowRight :size="16" /></button
          ><button
            class="journey-text-action"
            type="button"
            @click="emit('openXiaoxi')"
          >
            <Sparkles :size="16" />计划下一程
          </button>
        </section>
      </div>
    </div>
  </main>
</template>
