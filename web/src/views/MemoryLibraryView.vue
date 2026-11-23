<script setup lang="ts">
import {
  ArrowRight,
  BookOpen,
  CalendarDays,
  Compass,
  LockKeyhole,
  MapPin,
  Plus,
  Search,
  Sparkles,
} from 'lucide-vue-next'
import { computed, ref, watch } from 'vue'
import type { MapOverview, VisitedCity } from '../types'
const props = defineProps<{ overview: MapOverview }>()
const emit = defineEmits<{
  map: []
  compose: []
  selectCity: [city: VisitedCity]
  manualCheckIn: []
  studio: []
}>()
const query = ref('')
const onlyMemories = ref(false)
const year = ref<number | null>(null)
const summary = computed(() =>
  props.overview.year_summaries.find((s) => s.year === year.value),
)
const visibleCities = computed(() => {
  const activity = summary.value
    ? new Map(
        summary.value.cities.map((city) => [city.adcode, city.memory_count]),
      )
    : null
  const term = query.value.trim().toLocaleLowerCase()
  return props.overview.visited_cities
    .filter((city) => !activity || activity.has(city.adcode))
    .map((city) => ({
      ...city,
      memory_count: activity?.get(city.adcode) ?? city.memory_count,
    }))
    .filter(
      (city) =>
        (!onlyMemories.value || city.memory_count > 0) &&
        `${city.name_zh} ${city.name_en} ${city.province_zh}`
          .toLocaleLowerCase()
          .includes(term),
    )
    .sort((a, b) => b.last_visited_at.localeCompare(a.last_visited_at))
})
const filtered = computed(
  () => !!query.value || onlyMemories.value || year.value !== null,
)
watch(
  () => props.overview.year_summaries.map((s) => s.year),
  (years) => {
    if (year.value !== null && !years.includes(year.value)) year.value = null
  },
)
function resetFilters() {
  query.value = ''
  onlyMemories.value = false
  year.value = null
}
function date(value: string) {
  const parsed = new Date(value)
  return Number.isNaN(parsed.getTime())
    ? '日期待确认'
    : new Intl.DateTimeFormat('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
      }).format(parsed)
}
</script>
<template>
  <main class="memory-library journey-view" aria-label="旅行记忆书架">
    <div class="journey-scroll">
      <div class="journey-page">
        <header class="journey-hero">
          <div>
            <p class="journey-kicker">A LITTLE COLLECTION OF YOU</p>
            <h1>那些瞬间，<em>值得再读一遍。</em></h1>
            <p>按城市翻阅手记与影像，把散落的回忆慢慢连成故事。</p>
          </div>
          <button
            class="journey-primary"
            type="button"
            @click="emit('compose')"
          >
            <Sparkles :size="17" />整理旅行故事
          </button>
        </header>
        <nav class="journey-section-tabs" aria-label="旅程内容">
          <button type="button" @click="emit('map')">
            <Compass :size="17" />旅行足迹</button
          ><button class="active" type="button" aria-current="page">
            <BookOpen :size="17" />城市记忆
          </button>
        </nav>
        <section class="memory-library-intro">
          <div class="memory-intro-symbol">
            <BookOpen :size="34" /><span>KEEP<br />THE MOMENT.</span>
          </div>
          <div>
            <p class="journey-kicker">YOUR PRIVATE COLLECTION</p>
            <h2>每座城，都有属于你的一页。</h2>
            <p>
              <strong>{{ overview.stats.lit_cities }}</strong> 座城市 ·
              <strong>{{ overview.stats.memories }}</strong> 段记忆 ·
              <strong>{{ overview.stats.photos }}</strong> 张照片
            </p>
          </div>
          <span class="memory-private-label"
            ><LockKeyhole :size="14" />私人档案</span
          >
        </section>
        <div class="memory-library-toolbar">
          <div>
            <p class="journey-kicker">BROWSE BY CITY</p>
            <h2>
              城市索引 <span>{{ visibleCities.length }}</span>
            </h2>
          </div>
          <div class="memory-filter-controls">
            <label class="archive-search"
              ><Search :size="17" /><input
                v-model="query"
                aria-label="搜索记忆中的城市"
                placeholder="搜索城市或省份" /></label
            ><label class="atlas-year-filter"
              ><CalendarDays :size="16" /><span class="sr-only"
                >记忆活动年份</span
              ><select v-model="year">
                <option :value="null">全部年份</option>
                <option
                  v-for="item in overview.year_summaries"
                  :key="item.year"
                  :value="item.year"
                >
                  {{ item.year }} 年
                </option>
              </select></label
            ><label class="memory-only-filter"
              ><input v-model="onlyMemories" type="checkbox" />已有记忆</label
            >
          </div>
        </div>
        <p v-if="year !== null" class="memory-year-note">年份筛选城市索引中的活动与记忆数量；打开城市档案后，可翻阅该城全部记录。</p>
        <section
          v-if="visibleCities.length"
          class="memory-city-grid"
          aria-label="城市记忆索引"
        >
          <button
            v-for="(city, index) in visibleCities"
            :key="city.adcode"
            class="memory-city-card"
            type="button"
            :aria-label="`打开${city.name_zh}的城市记忆`"
            @click="emit('selectCity', city)"
          >
            <span class="memory-card-topline"
              ><span
                >CITY ARCHIVE / {{ String(index + 1).padStart(2, '0') }}</span
              ><MapPin :size="18" /></span
            ><span class="memory-city-initial" aria-hidden="true">{{
              city.name_zh.replace(/市$/, '').slice(0, 1)
            }}</span
            ><span class="memory-card-city"
              ><span>{{ city.province_zh }}</span
              ><strong>{{ city.name_zh }}</strong
              ><small v-if="city.name_en !== city.name_zh">{{
                city.name_en
              }}</small></span
            ><span class="memory-card-bottom"
              ><span
                ><BookOpen :size="15" />{{ city.memory_count }} 段{{
                  year ? `${year}年` : ''
                }}记忆</span
              ><ArrowRight :size="18" /></span
            ><span class="memory-card-date"
              >城市最近记录 · {{ date(city.last_visited_at) }}</span
            >
          </button>
        </section>
        <section v-else class="memory-library-empty">
          <span class="memory-empty-book"><BookOpen :size="45" /></span>
          <p class="journey-kicker">A NEW PAGE AWAITS</p>
          <h2>
            {{
              filtered
                ? '这次筛选，还没有找到记忆。'
                : '第一段记忆，从一次抵达开始。'
            }}
          </h2>
          <p>
            {{
              filtered
                ? '可以清除筛选，或选择其他城市与年份。'
                : '先记录去过的城市，再写下日期、心情和片刻。每一次保存，都由你确认。'
            }}
          </p>
          <button
            v-if="filtered"
            class="journey-secondary"
            type="button"
            @click="resetFilters"
          >
            清除筛选</button
          ><button
            v-else
            class="journey-primary"
            type="button"
            @click="emit('manualCheckIn')"
          >
            <Plus :size="16" />记录一座去过的城
          </button>
        </section>
        <section class="memory-pathway" aria-label="从记忆到创作">
          <article>
            <span>01</span>
            <div>
              <h3>留下原始记忆</h3>
              <p>在城市档案中写下日期与文字，添加自己的影像。</p>
            </div>
          </article>
          <article>
            <span>02</span>
            <div>
              <h3>和小曦整理故事</h3>
              <p>授权读取选定记录，核对、编辑后再确认保存。</p>
            </div>
          </article>
          <article>
            <span>03</span>
            <div>
              <h3>给照片一种新表达</h3>
              <p>从原照片进入风格创作，作品与来源一起保留。</p>
              <button
                type="button"
                class="journey-text-action"
                @click="emit('studio')"
              >
                打开创作空间<ArrowRight :size="14" />
              </button>
            </div>
          </article>
        </section>
      </div>
    </div>
  </main>
</template>
