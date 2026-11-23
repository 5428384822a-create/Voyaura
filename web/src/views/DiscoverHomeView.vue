<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import {
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  Camera,
  Check,
  Compass,
  ExternalLink,
  Map,
  MapPin,
  Search,
  Sparkles,
  Sun,
  Waves,
  Leaf,
  X,
} from 'lucide-vue-next'
import {
  destinations,
  destinationIntent,
  matchCities,
  searchableCities,
  type DiscoveryIntent,
  type TravelMood,
} from '../content/discovery'
import type { MapStats } from '../types'

withDefaults(defineProps<{ connected: boolean; stats: MapStats; cover?: 'city' | 'immersive' }>(), {
  cover: 'city',
})
const emit = defineEmits<{ plan: [intent: DiscoveryIntent]; map: []; stories: []; connect: [] }>()
const query = ref('')
const mood = ref<TravelMood>('all')
const showCities = ref(false)
const searchInput = ref<HTMLInputElement | null>(null)
const hero = ref<HTMLElement | null>(null)
const moods: Array<{ id: TravelMood; label: string }> = [
  { id: 'all', label: '全部灵感' },
  { id: 'sea', label: '海边放空' },
  { id: 'culture', label: '城市漫游' },
  { id: 'slow', label: '慢一点走' },
]
const visibleDestinations = computed(() =>
  destinations.filter(
    (d) => mood.value === 'all' || (d.moods as readonly string[]).includes(mood.value),
  ),
)
const choices = computed(() => {
  const matched = matchCities(query.value)
  return matched.length > 1 ? matched : searchableCities
})
function submitSearch() {
  if (!query.value.trim()) {
    showCities.value = true
    searchInput.value?.focus()
    return
  }
  const matched = matchCities(query.value.trim())
  if (matched.length === 1) chooseCity(matched[0]!.name, matched[0]!.adcode)
  else showCities.value = true
}
function clearSearch() {
  query.value = ''
  showCities.value = false
}
function searchSuggestion(text: string) {
  query.value = text
  submitSearch()
}
function chooseCity(name: string, adcode: string) {
  showCities.value = false
  const goal = query.value.trim()
    ? query.value.includes(name)
      ? query.value.trim()
      : `想去${name}，${query.value.trim()}`
    : `想去${name}旅行，帮我安排一段轻松的旅程。`
  emit('plan', { cityAdcode: adcode, goal, pace: 'relaxed' })
}
async function explore(text = '') {
  if (text) query.value = text
  showCities.value = true
  hero.value?.scrollIntoView?.({
    behavior: window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
      ? 'instant'
      : 'smooth',
    block: 'start',
  })
  await nextTick()
  searchInput.value?.focus({ preventScroll: true })
}
function exploreMood(id: TravelMood) {
  mood.value = id
  showCities.value = false
}
</script>

<template>
  <main class="discover-page" aria-label="旅行发现首页">
    <div class="discover-container">
      <section
        ref="hero"
        class="discover-hero"
        :class="{ 'discover-hero--immersive': cover === 'immersive' }"
        aria-labelledby="discover-title"
      >
        <div class="hero-image-wrap" aria-hidden="true">
          <img
            src="/discover/xiamen-hero.webp"
            alt=""
            class="hero-image"
            fetchpriority="high"
            width="1800"
            height="800"
          />
          <div class="hero-light"></div>
        </div>
        <div class="hero-content">
          <p class="hero-kicker"><span></span> FIND YOUR NEXT CHAPTER</p>
          <h1 id="discover-title">下一段旅程，<br />从心动开始<span>。</span></h1>
          <p class="hero-description">去一座想去的城，把沿途的风景慢慢收藏。</p>
          <div class="hero-search-area">
            <form
              class="discovery-search"
              role="search"
              @submit.prevent="submitSearch"
              @keydown.esc="showCities = false"
            >
              <Search :size="22" aria-hidden="true" />
              <input
                id="discover-search"
                ref="searchInput"
                v-model="query"
                type="search"
                maxlength="300"
                autocomplete="off"
                aria-label="旅行搜索"
                placeholder="目的地、景点，或这次旅行的想法"
              />
              <button
                v-if="query"
                class="clear-search"
                type="button"
                aria-label="清空搜索"
                @click="clearSearch"
              >
                <X :size="15" />
              </button>
              <button class="search-go" type="submit" aria-label="搜索并规划">
                <span>开始探索</span><ArrowRight :size="18" />
              </button>
            </form>
            <section v-if="showCities" class="search-city-panel" aria-label="选择旅行目的地">
              <div>
                <strong>{{ query ? '先选一座城，把想法带上' : '想从哪座城市开始？' }}</strong
                ><button type="button" aria-label="收起目的地选择" @click="showCities = false">
                  <X :size="16" />
                </button>
              </div>
              <p v-if="query">你的旅行想法会一并带入计划，之后还可以调整。</p>
              <div class="search-city-options">
                <button
                  v-for="city in choices"
                  :key="city.adcode"
                  type="button"
                  @click="chooseCity(city.name, city.adcode)"
                >
                  <MapPin :size="15" />{{ city.name }}<ArrowUpRight :size="14" />
                </button>
              </div>
            </section>
          </div>
          <div class="hero-suggestions">
            <span>试试</span
            ><button
              type="button"
              @click="searchSuggestion('厦门两日慢游')"
            >
              厦门两日慢游</button
            ><i></i
            ><button
              type="button"
              @click="searchSuggestion('杭州西湖散步')"
            >
              西湖边走走</button
            ><i></i
            ><button type="button" @click="explore('想看看自然，行程轻松一点')">
              给旅途留点空白
            </button>
          </div>
        </div>
        <div class="hero-location">
          <MapPin :size="14" /><span>中国 · 厦门</span><i></i><span>海风里的鼓浪屿</span>
        </div>
        <div class="hero-type"><Compass :size="13" /><span>海风与慢生活</span></div>
      </section>

      <section class="discover-shortcuts" aria-label="旅行快捷入口">
        <button type="button" @click="explore()">
          <span class="shortcut-icon peach"><MapPin :size="22" /></span
          ><span><strong>目的地</strong><small>找一座心动的城</small></span
          ><ArrowUpRight class="shortcut-arrow" :size="16" />
        </button>
        <button type="button" @click="emit('plan', { goal: '', pace: 'relaxed' })">
          <span class="shortcut-icon rose"><CalendarDays :size="22" /></span
          ><span><strong>规划行程</strong><small>把想法安排妥当</small></span
          ><ArrowUpRight class="shortcut-arrow" :size="16" />
        </button>
        <button type="button" @click="emit('map')">
          <span class="shortcut-icon mint"><Map :size="22" /></span
          ><span><strong>旅行地图</strong><small>收藏每一次抵达</small></span
          ><ArrowUpRight class="shortcut-arrow" :size="16" />
        </button>
        <button type="button" @click="emit('stories')">
          <span class="shortcut-icon sand"><Camera :size="22" /></span
          ><span><strong>旅行记忆</strong><small>留下沿途的故事</small></span
          ><ArrowUpRight class="shortcut-arrow" :size="16" />
        </button>
        <button type="button" @click="explore('想和小曦一起规划，慢慢探索一座城')">
          <span class="shortcut-icon lilac"><Sparkles :size="22" /></span
          ><span><strong>小曦同行</strong><small>陪你发现与记录</small></span
          ><ArrowUpRight class="shortcut-arrow" :size="16" />
        </button>
      </section>

      <div class="discover-lower-grid">
        <section class="destination-section" aria-labelledby="destination-heading">
          <header class="discover-section-heading">
            <div>
              <p class="section-eyebrow">PLACES TO FALL FOR</p>
              <h2 id="destination-heading">总有一座城，让你想出发</h2>
              <p>从一份旅行灵感开始，慢慢走进当地的日常。</p>
            </div>
            <button class="quiet-link more-destinations" type="button" @click="explore()">
              更多目的地<ArrowUpRight :size="16" />
            </button>
          </header>
          <div class="mood-filters" role="group" aria-label="旅行灵感主题">
            <button
              v-for="item in moods"
              :key="item.id"
              type="button"
              :class="{ active: mood === item.id }"
              :aria-pressed="mood === item.id"
              @click="exploreMood(item.id)"
            >
              <span v-if="mood === item.id" class="filter-dot"></span>{{ item.label }}
            </button>
          </div>
          <div class="destination-grid">
            <button
              v-for="(destination, index) in visibleDestinations"
              :key="destination.id"
              type="button"
              class="destination-card"
              :aria-label="`规划${destination.name}旅行`"
              @click="emit('plan', destinationIntent(destination.id))"
            >
              <span class="destination-photo"
                ><img
                  :src="destination.image"
                  :alt="destination.imageAlt"
                  :loading="index === 0 ? 'eager' : 'lazy'"
                  decoding="async"
                  width="960"
                  height="640" /><span class="destination-photo-shade"></span
                ><span class="destination-english">{{ destination.english }}</span
                ><span class="destination-photo-arrow"><ArrowUpRight :size="19" /></span
              ></span>
              <span class="destination-content"
                ><span class="destination-title"
                  ><strong>{{ destination.name }}</strong
                  ><span>{{ destination.headline }}</span></span
                ><span class="destination-description">{{ destination.description }}</span
                ><span class="destination-tags"
                  ><span v-for="tag in destination.tags" :key="tag">{{ tag }}</span></span
                ></span
              >
            </button>
          </div>
          <div class="travel-map-invite">
            <div class="map-invite-symbol" aria-hidden="true">
              <Map :size="33" /><span></span><MapPin :size="18" />
            </div>
            <div class="map-invite-copy">
              <h3>每一次抵达，都有故事。</h3>
              <p v-if="connected">
                已经点亮 {{ stats.lit_cities }} 座城市，留下 {{ stats.memories }} 段旅行记忆。
              </p>
              <p v-else>在你的旅行地图里，收藏城市、照片与回忆。</p>
            </div>
            <button type="button" @click="emit('map')">
              打开我的地图<ArrowRight :size="16" />
            </button>
          </div>
        </section>

        <aside class="discovery-companion" aria-label="和小曦一起规划">
          <div class="companion-art" aria-hidden="true">
            <div class="companion-orbit"></div>
            <span class="companion-ray ray-one"></span><span class="companion-ray ray-two"></span
            ><span class="companion-ray ray-three"></span>
            <div class="companion-sun"><Sun :size="36" :stroke-width="1.25" /></div>
            <span class="companion-spark"><Sparkles :size="17" /></span
            ><span class="companion-path"><Compass :size="19" /></span>
          </div>
          <p class="companion-eyebrow">YOUR TRAVEL COMPANION</p>
          <h2>说说想法，<br />剩下的，一起安排。</h2>
          <p class="companion-description">
            我是小曦。想去哪里、喜欢什么，<br class="desktop-break" />都可以成为一段旅程的开始。
          </p>
          <div class="companion-prompts">
            <button type="button" @click="explore('想去海边放空两天，看看海，走走老街')">
              <Waves :size="15" />想去海边放空两天<ArrowUpRight :size="14" /></button
            ><button type="button" @click="explore('喜欢自然风光，想规划一次轻松的周末旅行')">
              <Leaf :size="15" />给周末，换一种风景<ArrowUpRight :size="14" />
            </button>
          </div>
          <button
            class="companion-start"
            type="button"
            @click="emit('plan', { goal: '', pace: 'relaxed' })"
          >
            <Sparkles :size="16" />和小曦规划旅程<ArrowRight :size="17" />
          </button>
          <p class="companion-note"><Check :size="12" />先成为草案，每一步由你确认</p>
        </aside>
      </div>
      <footer class="discover-footer">
        <p>Voyaura <span>·</span> Plan the journey. Shape the story.</p>
        <a href="/discover/credits.html" target="_blank" rel="noopener noreferrer"
          >影像署名与许可<ExternalLink :size="12"
        /></a>
      </footer>
    </div>
  </main>
</template>

<style scoped>
.discover-page {
  position: absolute;
  inset: var(--product-header-height) 0 0;
  overflow: auto;
  background: var(--page-bg);
  scroll-behavior: smooth;
  scroll-padding-top: 24px;
}
.discover-container {
  width: min(1320px, calc(100% - 80px));
  margin: auto;
  padding: 30px 0 0;
}
.discover-hero {
  position: relative;
  min-height: 405px;
  border-radius: 20px;
  background: #eaf1f2;
  isolation: isolate;
}
.hero-image-wrap {
  position: absolute;
  inset: 0;
  border-radius: 20px;
  overflow: hidden;
  z-index: -1;
}
.hero-image {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 75% 48%;
}
.hero-light {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      90deg,
      rgba(249, 248, 243, 0.99) 0%,
      rgba(249, 248, 243, 0.96) 22%,
      rgba(249, 248, 243, 0.72) 39%,
      rgba(249, 248, 243, 0.05) 65%
    ),
    linear-gradient(0deg, rgba(24, 48, 48, 0.12), transparent 35%);
}
.hero-content {
  position: relative;
  width: 620px;
  max-width: 75%;
  padding: 42px 0 39px 46px;
}
.hero-kicker {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 14px;
  font-size: 10px;
  letter-spacing: 2px;
  color: #8b8a7e;
  font-weight: 650;
}
.hero-kicker > span {
  display: block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f1774c;
}
.hero-content h1 {
  font-size: 48px;
  line-height: 1.24;
  letter-spacing: -1.8px;
  font-weight: 650;
  color: #26332e;
  margin: 0 0 15px;
}
.hero-content h1 > span {
  color: var(--brand-orange);
}
.hero-description {
  color: #69736c;
  font-size: 14px;
  line-height: 1.8;
  margin: 0 0 24px;
}
.hero-search-area {
  position: relative;
  z-index: 25;
}
.discovery-search {
  display: flex;
  align-items: center;
  gap: 11px;
  height: 58px;
  padding: 6px 7px 6px 18px;
  border: 1px solid #ffffffc9;
  border-radius: 12px;
  background: #fffffff5;
  box-shadow: 0 8px 30px #344d4712;
}
.discovery-search > svg {
  color: #8b9990;
  flex: none;
}
.discovery-search input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  background: transparent;
  font-size: 14px;
  line-height: 1.6;
  color: #34443c;
}
.discovery-search input::placeholder {
  color: #919a93;
}
.discovery-search input::-webkit-search-cancel-button {
  display: none;
}
.discovery-search:focus-within {
  outline: 2px solid #f3936e66;
  outline-offset: 2px;
}
.search-go {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  flex: none;
  height: 44px;
  padding: 0 17px;
  background: var(--brand-button);
  border: 0;
  border-radius: 9px;
  color: white;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.search-go:hover {
  background: #bc4020;
}
.clear-search {
  display: grid;
  place-items: center;
  padding: 4px;
  border: 0;
  background: transparent;
  color: #939c95;
  cursor: pointer;
}
.hero-suggestions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 9px;
  margin-top: 14px;
  color: #879087;
  font-size: 11px;
}
.hero-suggestions > span {
  font-size: 10px;
  color: #8a938a;
}
.hero-suggestions button {
  border: 0;
  background: transparent;
  padding: 3px 0;
  color: #67756b;
  font-size: 11px;
  cursor: pointer;
}
.hero-suggestions button:hover {
  color: var(--brand-ink-orange);
}
.hero-suggestions i {
  width: 2px;
  height: 2px;
  border-radius: 50%;
  background: #a4afa6;
}
.hero-location {
  display: flex;
  align-items: center;
  gap: 7px;
  position: absolute;
  right: 24px;
  bottom: 22px;
  padding: 9px 12px;
  border: 1px solid #ffffff6b;
  border-radius: 20px;
  background: #ffffffe0;
  backdrop-filter: blur(10px);
  color: #4c6258;
  font-size: 11px;
}
.hero-location i {
  width: 1px;
  height: 10px;
  background: #c4cec5;
}
.hero-chapter {
  position: absolute;
  right: 24px;
  top: 23px;
  display: flex;
  gap: 5px;
  align-items: center;
  color: white;
  text-shadow: 0 1px 8px #173e4a66;
}
.hero-chapter span {
  margin-right: 8px;
  font-size: 10px;
  letter-spacing: 1px;
}
.hero-chapter i {
  width: 5px;
  height: 5px;
  border-radius: 5px;
  background: #ffffff80;
}
.hero-chapter i.active {
  width: 17px;
  background: white;
}
.search-city-panel {
  position: absolute;
  top: calc(100% + 10px);
  left: 0;
  right: 0;
  padding: 18px;
  border: 1px solid #ece7df;
  border-radius: 12px;
  background: #fffefa;
  box-shadow: 0 15px 40px #213d3524;
}
.search-city-panel > div:first-child {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.search-city-panel strong {
  font-size: 14px;
  font-weight: 600;
}
.search-city-panel > div:first-child > button {
  border: 0;
  background: transparent;
  color: #8b9389;
  cursor: pointer;
  padding: 5px;
}
.search-city-panel > p {
  font-size: 12px;
  color: #8b9389;
  line-height: 1.7;
  margin: 7px 0 15px;
}
.search-city-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 12px;
}
.search-city-options > button {
  display: flex;
  align-items: center;
  gap: 7px;
  border: 1px solid #eee9e0;
  border-radius: 8px;
  padding: 11px 9px;
  background: #fbfaf5;
  color: #68776b;
  font-size: 13px;
  cursor: pointer;
}
.search-city-options > button > svg:first-child {
  color: #e36c45;
}
.search-city-options > button > svg:last-child {
  margin-left: auto;
  color: #a6afa4;
}
.search-city-options > button:hover {
  background: #fff0e8;
  border-color: #f1cbb8;
}
.discover-shortcuts {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0;
  margin: 21px 0 33px;
  padding: 18px 2px;
  background: #fffefa;
  border: 1px solid #efebe4;
  border-radius: 14px;
  box-shadow: 0 3px 10px #2c3c2a02;
}
.discover-shortcuts > button {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 4px 22px;
  border: 0;
  border-right: 1px solid #eeeae3;
  background: transparent;
  text-align: left;
  cursor: pointer;
  min-width: 0;
}
.discover-shortcuts > button:last-child {
  border-right: 0;
}
.shortcut-icon {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  flex: none;
  border-radius: 14px;
  transition: transform 0.2s;
}
.peach {
  color: #df653e;
  background: #fff0e7;
}
.rose {
  color: #dc706a;
  background: #fcecee;
}
.mint {
  color: #4c9a84;
  background: #e9f3ee;
}
.sand {
  color: #c28b37;
  background: #fcf2df;
}
.lilac {
  color: #9880c4;
  background: #f1ecf8;
}
.discover-shortcuts > button:hover .shortcut-icon {
  transform: translateY(-3px);
}
.discover-shortcuts > button > span:nth-child(2) {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}
.discover-shortcuts strong {
  font-size: 14px;
  font-weight: 600;
  color: #3e4b43;
  white-space: nowrap;
}
.discover-shortcuts small {
  font-size: 10px;
  color: #959c92;
  white-space: nowrap;
}
.shortcut-arrow {
  display: none;
  flex: none;
  margin-left: auto;
  color: #b4bbb0;
}
.discover-lower-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 28px;
  align-items: stretch;
}
.destination-section {
  min-width: 0;
}
.discover-section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin: 0 0 19px;
}
.section-eyebrow {
  font-size: 9px;
  letter-spacing: 1.6px;
  color: #a2a396;
  font-weight: 650;
  margin: 0 0 8px;
}
.discover-section-heading h2 {
  font-size: 23px;
  line-height: 1.45;
  letter-spacing: -0.5px;
  font-weight: 650;
  color: #303e35;
  margin: 0 0 7px;
}
.discover-section-heading > div > p:last-child {
  font-size: 12px;
  color: #8b9589;
  line-height: 1.7;
  margin: 0;
}
.quiet-link {
  display: flex;
  align-items: center;
  gap: 5px;
  white-space: nowrap;
  padding: 7px 0;
  border: 0;
  background: transparent;
  color: #85917f;
  font-size: 11px;
  cursor: pointer;
}
.quiet-link:hover {
  color: var(--brand-ink-orange);
}
.mood-filters {
  display: flex;
  gap: 7px;
  align-items: center;
  margin: 0 0 19px;
  flex-wrap: wrap;
}
.mood-filters > button {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  min-height: 34px;
  border: 1px solid transparent;
  border-radius: 18px;
  background: transparent;
  font-size: 11px;
  color: #8d9589;
  cursor: pointer;
}
.mood-filters > button.active {
  color: var(--brand-ink-orange);
  background: #fff0e7;
  border-color: #f3d3c1;
  font-weight: 600;
}
.filter-dot {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: #e97c54;
}
.destination-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 17px;
}
.destination-card {
  display: block;
  overflow: hidden;
  padding: 0;
  border: 1px solid #e9e5dc;
  border-radius: 12px;
  background: #fffefa;
  text-align: left;
  cursor: pointer;
  box-shadow: 0 5px 20px #414b3a03;
  transition:
    transform 0.25s,
    box-shadow 0.25s;
}
.destination-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 25px #374a3914;
}
.destination-photo {
  position: relative;
  display: block;
  aspect-ratio: 1.47;
  overflow: hidden;
}
.destination-photo > img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.55s;
}
.destination-card:hover .destination-photo > img {
  transform: scale(1.04);
}
.destination-photo-shade {
  position: absolute;
  inset: 0;
  background: linear-gradient(0deg, #18362b36, transparent 50%);
}
.destination-english {
  position: absolute;
  left: 16px;
  bottom: 13px;
  color: #fff9f1;
  font-size: 9px;
  letter-spacing: 2.5px;
  font-weight: 650;
  text-shadow: 0 1px 4px #173d2d33;
}
.destination-photo-arrow {
  position: absolute;
  right: 10px;
  top: 10px;
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #ffffffe8;
  color: #607467;
}
.destination-content {
  display: block;
  padding: 17px 15px 15px;
}
.destination-title {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}
.destination-title > strong {
  font-size: 20px;
  font-weight: 650;
  color: #344237;
  line-height: 1.25;
}
.destination-title > span {
  font-size: 12px;
  color: #73806e;
}
.destination-description {
  display: block;
  font-size: 11px;
  line-height: 1.8;
  color: #939b8d;
  margin-bottom: 14px;
}
.destination-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.destination-tags > span {
  font-size: 9px;
  line-height: 1.5;
  padding: 4px 6px;
  color: #829075;
  background: #f2f4ea;
  border-radius: 4px;
}
.discovery-companion {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 24px 23px 22px;
  border: 1px solid #ebe3d3;
  border-radius: 14px;
  background: linear-gradient(145deg, #fff7e8, #faf5e9 45%, #f1f2e7);
  overflow: hidden;
}
.companion-art {
  position: relative;
  width: 100%;
  height: 105px;
  flex: none;
  margin-bottom: 18px;
}
.companion-orbit {
  position: absolute;
  width: 118px;
  height: 118px;
  left: 50%;
  top: -8px;
  transform: translateX(-50%);
  border: 1px solid #e9dfbf;
  border-radius: 50%;
}
.companion-orbit:after {
  content: '';
  position: absolute;
  inset: 13px;
  border: 1px dashed #e7debd;
  border-radius: 50%;
}
.companion-sun {
  position: absolute;
  left: 50%;
  top: 20px;
  transform: translateX(-50%);
  display: grid;
  place-items: center;
  width: 64px;
  height: 64px;
  color: #c99a44;
  background: linear-gradient(145deg, #fff3c5, #f6e0a6);
  border: 5px solid #fff7de;
  border-radius: 50%;
  box-shadow: 0 10px 25px #b9a57914;
}
.companion-spark {
  position: absolute;
  left: 24%;
  top: 4px;
  display: grid;
  place-items: center;
  color: #dfa14d;
}
.companion-path {
  position: absolute;
  right: 13%;
  bottom: 0;
  display: grid;
  place-items: center;
  width: 33px;
  height: 33px;
  border: 1px solid #e8d9b8;
  background: #fff9e7;
  border-radius: 10px;
  color: #a0a06f;
  transform: rotate(12deg);
}
.companion-ray {
  position: absolute;
  width: 5px;
  height: 5px;
  background: #e6b66b;
  border-radius: 50%;
}
.ray-one {
  left: 9%;
  top: 44px;
}
.ray-two {
  right: 18%;
  top: 11px;
  width: 3px;
  height: 3px;
}
.ray-three {
  left: 25%;
  bottom: 4px;
  width: 3px;
  height: 3px;
}
.companion-eyebrow {
  font-size: 8px;
  letter-spacing: 1.4px;
  color: #a89978;
  margin: 0 0 12px;
  font-weight: 650;
}
.discovery-companion h2 {
  font-size: 23px;
  line-height: 1.55;
  font-weight: 600;
  letter-spacing: -0.6px;
  margin: 0 0 12px;
  color: #564e3a;
}
.companion-description {
  font-size: 12px;
  line-height: 1.9;
  color: #9a927c;
  margin: 0 0 19px;
}
.companion-prompts {
  display: flex;
  flex-direction: column;
  gap: 9px;
  width: 100%;
  margin-top: auto;
  margin-bottom: 20px;
}
.companion-prompts > button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 11px 9px;
  border: 1px solid #e9e0cb;
  border-radius: 8px;
  color: #8f8368;
  background: #fffdf47d;
  font-size: 11px;
  cursor: pointer;
  text-align: left;
}
.companion-prompts > button > svg {
  margin-left: auto;
  color: #b4a689;
  flex: none;
}
.companion-start {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 7px;
  width: 100%;
  padding: 13px 8px;
  border: 0;
  border-radius: 8px;
  color: white;
  background: var(--brand-button);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.2s;
}
.companion-start:hover {
  background: #bc4020;
}
.companion-start > svg:last-child {
  margin-left: auto;
}
.companion-note {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  gap: 4px;
  margin: 12px 0 0;
  color: #a89d81;
  font-size: 9px;
}
.travel-map-invite {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-top: 24px;
  padding: 23px 21px;
  border: 1px solid #e4e9de;
  border-radius: 12px;
  background: linear-gradient(100deg, #edf2e9, #f4f5ec 65%);
}
.map-invite-symbol {
  position: relative;
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  flex: none;
  color: #829d7e;
}
.map-invite-symbol > svg:last-child {
  position: absolute;
  right: -1px;
  top: -1px;
  color: #d48b57;
  fill: #faf6ed;
}
.map-invite-copy {
  min-width: 0;
}
.map-invite-copy h3 {
  font-size: 15px;
  font-weight: 600;
  color: #5d7155;
  margin: 0 0 7px;
}
.map-invite-copy p {
  font-size: 11px;
  color: #8e9d80;
  margin: 0;
  line-height: 1.7;
}
.travel-map-invite > button {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
  margin-left: auto;
  padding: 11px 12px;
  border: 1px solid #cddac3;
  border-radius: 7px;
  background: #fffffa80;
  color: #718566;
  font-size: 11px;
  cursor: pointer;
}
.travel-map-invite > button:hover {
  background: #fffef8;
}
.discover-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 29px 0 24px;
  color: #a4aa9c;
  font-size: 10px;
}
.discover-footer p {
  margin: 0;
}
.discover-footer p > span {
  margin: 0 7px;
}
.discover-footer a {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #9da68f;
  text-decoration: none;
  font-size: 10px;
}
.discover-footer a:hover {
  color: #60775c;
}
@media (min-width: 1600px) {
  .discover-container {
    padding-top: 36px;
  }
  .discover-hero {
    min-height: 440px;
  }
  .hero-content {
    padding: 50px 0 46px 55px;
  }
  .hero-content h1 {
    font-size: 52px;
  }
  .discover-lower-grid {
    grid-template-columns: minmax(0, 1fr) 290px;
  }
}
@media (min-width: 900px) and (max-width: 1150px) {
  .discover-container {
    width: calc(100% - 48px);
  }
  .discover-shortcuts > button {
    padding: 4px 13px;
    gap: 9px;
  }
  .shortcut-icon {
    width: 38px;
    height: 38px;
    border-radius: 12px;
  }
  .discover-shortcuts strong {
    font-size: 13px;
  }
  .discover-shortcuts small {
    font-size: 9px;
  }
  .discover-lower-grid {
    grid-template-columns: minmax(0, 1fr) 250px;
    gap: 20px;
  }
  .destination-grid {
    gap: 12px;
  }
  .destination-content {
    padding: 14px 11px;
  }
  .destination-title > strong {
    font-size: 19px;
  }
  .destination-description {
    font-size: 10px;
  }
  .discovery-companion {
    padding: 23px 18px;
  }
  .discovery-companion h2 {
    font-size: 21px;
  }
  .companion-start {
    font-size: 11px;
  }
  .travel-map-invite {
    padding: 20px 15px;
    gap: 10px;
  }
  .travel-map-invite > button {
    padding: 9px;
    font-size: 10px;
  }
}
@media (max-width: 899px) {
  .discover-page {
    bottom: calc(68px + env(safe-area-inset-bottom));
    scroll-padding-top: 16px;
  }
  .discover-container {
    width: calc(100% - 40px);
    padding-top: 20px;
  }
  .discover-hero {
    min-height: 365px;
  }
  .hero-content {
    width: 570px;
    max-width: 85%;
    padding: 34px 0 32px 30px;
  }
  .hero-content h1 {
    font-size: 40px;
  }
  .hero-light {
    background: linear-gradient(90deg, #f9f8f3f5 0%, #f9f8f3d9 30%, #f9f8f32e 80%);
  }
  .hero-kicker {
    font-size: 8px;
    letter-spacing: 1.5px;
  }
  .hero-description {
    font-size: 13px;
  }
  .hero-location {
    font-size: 10px;
    right: 16px;
    bottom: 16px;
  }
  .hero-chapter {
    right: 20px;
    top: 20px;
  }
  .discover-shortcuts {
    margin: 17px 0 28px;
    padding: 15px 6px;
  }
  .discover-shortcuts > button {
    flex-direction: column;
    gap: 9px;
    padding: 0 4px;
    border-right: 0;
    text-align: center;
  }
  .discover-shortcuts small {
    display: none;
  }
  .discover-shortcuts > button > span:nth-child(2) {
    gap: 0;
  }
  .discover-shortcuts strong {
    font-size: 12px;
    font-weight: 500;
  }
  .shortcut-icon {
    width: 42px;
    height: 42px;
    border-radius: 50%;
  }
  .discover-lower-grid {
    grid-template-columns: 1fr;
    gap: 26px;
  }
  .discovery-companion {
    display: grid;
    grid-template-columns: 120px minmax(0, 1fr);
    column-gap: 22px;
    padding: 25px;
  }
  .companion-art {
    grid-row: 1/5;
    height: 120px;
    align-self: center;
    margin: 0;
  }
  .discovery-companion .companion-eyebrow,
  .discovery-companion h2,
  .companion-description,
  .companion-start {
    grid-column: 2;
  }
  .discovery-companion h2 {
    font-size: 22px;
  }
  .discovery-companion h2 > br {
    display: none;
  }
  .companion-description {
    margin-bottom: 15px;
  }
  .desktop-break {
    display: none;
  }
  .companion-prompts {
    display: none;
  }
  .companion-start {
    max-width: 290px;
    justify-content: center;
    padding: 12px;
    font-size: 13px;
  }
  .companion-note {
    grid-column: 2;
    justify-content: flex-start;
    font-size: 10px;
  }
  .discover-section-heading h2 {
    font-size: 22px;
  }
  .discover-footer {
    padding: 25px 0 20px;
  }
}
@media (max-width: 600px) {
  .discover-container {
    width: calc(100% - 32px);
    padding-top: 15px;
  }
  .discover-hero {
    min-height: 333px;
    border-radius: 15px;
  }
  .hero-image-wrap {
    border-radius: 15px;
  }
  .hero-image {
    object-position: 71% 46%;
  }
  .hero-light {
    background:
      linear-gradient(90deg, #faf8f2f5 0%, #faf8f2c4 37%, #faf8f23d 82%),
      linear-gradient(0deg, #faf8f2e8 0%, #faf8f200 30%);
  }
  .hero-content {
    width: 100%;
    max-width: 100%;
    padding: 28px 21px 34px;
  }
  .hero-kicker {
    font-size: 7px;
    letter-spacing: 1.2px;
    gap: 6px;
    margin-bottom: 12px;
  }
  .hero-kicker > span {
    width: 5px;
    height: 5px;
  }
  .hero-content h1 {
    font-size: 32px;
    line-height: 1.34;
    letter-spacing: -0.8px;
    margin-bottom: 11px;
  }
  .hero-description {
    font-size: 11px;
    line-height: 1.8;
    max-width: 230px;
    margin-bottom: 22px;
  }
  .discovery-search {
    height: 51px;
    padding: 5px 5px 5px 12px;
    gap: 8px;
    border-radius: 10px;
  }
  .discovery-search > svg {
    width: 18px;
    height: 18px;
  }
  .discovery-search input {
    font-size: 12px;
  }
  .search-go {
    height: 39px;
    width: 40px;
    padding: 0;
    border-radius: 7px;
    gap: 0;
  }
  .search-go > span {
    display: none;
  }
  .hero-suggestions {
    gap: 7px;
    margin-top: 12px;
  }
  .hero-suggestions button {
    font-size: 9px;
    line-height: 1.6;
  }
  .hero-suggestions > span {
    font-size: 9px;
  }
  .hero-location {
    bottom: 12px;
    left: 22px;
    right: auto;
    font-size: 8px;
    gap: 5px;
    padding: 0;
    border: 0;
    border-radius: 0;
    background: transparent;
    color: #788b7e;
    backdrop-filter: none;
  }
  .hero-location > svg {
    width: 10px;
    height: 10px;
  }
  .hero-location i {
    height: 8px;
    background: #aebeb0;
  }
  .hero-chapter {
    top: 25px;
    right: 18px;
    gap: 3px;
  }
  .hero-chapter span {
    display: none;
  }
  .hero-chapter i {
    width: 3px;
    height: 3px;
  }
  .hero-chapter i.active {
    width: 11px;
  }
  .discover-shortcuts {
    margin: 15px 0 27px;
    padding: 15px 4px 14px;
    border-radius: 12px;
  }
  .shortcut-icon {
    width: 36px;
    height: 36px;
  }
  .shortcut-icon > svg {
    width: 19px;
    height: 19px;
  }
  .discover-shortcuts > button {
    gap: 8px;
  }
  .discover-shortcuts strong {
    font-size: 10px;
    letter-spacing: 0;
  }
  .discover-section-heading {
    gap: 8px;
    margin-bottom: 15px;
  }
  .section-eyebrow {
    font-size: 7px;
    letter-spacing: 1.3px;
    margin-bottom: 7px;
  }
  .discover-section-heading h2 {
    font-size: 20px;
    letter-spacing: -0.6px;
    margin-bottom: 6px;
  }
  .discover-section-heading > div > p:last-child {
    font-size: 10px;
    line-height: 1.8;
  }
  .more-destinations {
    font-size: 0;
    min-width: 32px;
    height: 32px;
    justify-content: center;
    border: 1px solid #e6e6db;
    border-radius: 50%;
    padding: 0;
  }
  .more-destinations > svg {
    width: 16px;
    height: 16px;
  }
  .mood-filters {
    flex-wrap: nowrap;
    gap: 2px;
    margin-bottom: 16px;
  }
  .mood-filters > button {
    padding: 7px 9px;
    min-height: 31px;
    font-size: 10px;
    gap: 4px;
    white-space: nowrap;
  }
  .destination-grid {
    display: flex;
    gap: 13px;
    margin-right: -16px;
    padding: 3px 16px 12px 0;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
  }
  .destination-grid::-webkit-scrollbar {
    display: none;
  }
  .destination-card {
    flex: 0 0 226px;
    scroll-snap-align: start;
    border-radius: 12px;
    box-shadow: none;
  }
  .destination-card:hover {
    transform: none;
  }
  .destination-photo {
    aspect-ratio: 1.38;
  }
  .destination-content {
    padding: 15px 14px;
  }
  .destination-title > strong {
    font-size: 21px;
  }
  .destination-title > span {
    font-size: 12px;
  }
  .destination-description {
    font-size: 10px;
    margin-bottom: 12px;
  }
  .destination-tags > span {
    font-size: 9px;
  }
  .destination-english {
    font-size: 8px;
    left: 13px;
    bottom: 12px;
  }
  .travel-map-invite {
    position: relative;
    align-items: flex-start;
    gap: 11px;
    margin-top: 14px;
    padding: 17px 15px 18px;
    border-radius: 12px;
  }
  .map-invite-symbol {
    width: 37px;
    height: 41px;
  }
  .map-invite-symbol > svg:first-child {
    width: 30px;
    height: 30px;
  }
  .map-invite-symbol > svg:last-child {
    width: 15px;
    height: 15px;
  }
  .map-invite-copy {
    padding-top: 4px;
    padding-bottom: 32px;
  }
  .map-invite-copy h3 {
    font-size: 14px;
    margin-bottom: 7px;
  }
  .map-invite-copy p {
    font-size: 10px;
    line-height: 1.8;
  }
  .travel-map-invite > button {
    position: absolute;
    left: 63px;
    bottom: 15px;
    border: 0;
    background: transparent;
    padding: 0;
    gap: 5px;
    font-size: 10px;
    min-height: 22px;
  }
  .travel-map-invite > button > svg {
    width: 13px;
    height: 13px;
  }
  .discovery-companion {
    padding: 21px 18px;
    column-gap: 14px;
    grid-template-columns: 74px minmax(0, 1fr);
    border-radius: 12px;
  }
  .companion-art {
    height: 95px;
  }
  .companion-orbit {
    width: 78px;
    height: 78px;
    top: 5px;
  }
  .companion-orbit:after {
    inset: 9px;
  }
  .companion-sun {
    width: 49px;
    height: 49px;
    top: 20px;
    border-width: 4px;
  }
  .companion-sun > svg {
    width: 29px;
    height: 29px;
  }
  .companion-spark {
    left: -4%;
    top: 2px;
  }
  .companion-path {
    width: 25px;
    height: 25px;
    right: -3%;
    bottom: 7px;
    border-radius: 8px;
  }
  .companion-path > svg {
    width: 15px;
    height: 15px;
  }
  .ray-one {
    left: -10%;
  }
  .ray-two {
    right: 3%;
    top: 3px;
  }
  .companion-eyebrow {
    font-size: 6px;
    letter-spacing: 1px;
    margin-bottom: 8px;
  }
  .discovery-companion h2 {
    font-size: 18px;
    letter-spacing: -0.4px;
    line-height: 1.5;
    margin-bottom: 8px;
  }
  .discovery-companion h2 > br {
    display: none;
  }
  .companion-description {
    font-size: 10px;
    line-height: 1.9;
    margin-bottom: 13px;
  }
  .companion-start {
    padding: 11px 9px;
    font-size: 11px;
    min-height: 39px;
    border-radius: 7px;
    gap: 6px;
  }
  .companion-start > svg:first-child {
    width: 14px;
    height: 14px;
  }
  .companion-start > svg:last-child {
    width: 14px;
    height: 14px;
  }
  .companion-note {
    font-size: 8px;
    margin-top: 9px;
  }
  .companion-note > svg {
    width: 10px;
    height: 10px;
  }
  .discover-footer {
    align-items: flex-start;
    gap: 10px;
    padding: 23px 0 19px;
    font-size: 8px;
  }
  .discover-footer p {
    max-width: 200px;
    line-height: 1.8;
  }
  .discover-footer p > span {
    margin: 0 4px;
  }
  .discover-footer a {
    font-size: 8px;
    gap: 3px;
    white-space: nowrap;
    line-height: 1.8;
  }
  .discover-footer a > svg {
    width: 10px;
    height: 10px;
  }
  .search-city-panel {
    padding: 14px;
    border-radius: 10px;
  }
  .search-city-panel strong {
    font-size: 13px;
  }
  .search-city-panel > p {
    font-size: 11px;
    line-height: 1.8;
  }
  .search-city-options {
    gap: 7px;
  }
  .search-city-options > button {
    font-size: 12px;
    padding: 12px 7px;
    gap: 4px;
  }
  .search-city-options > button > svg:last-child {
    width: 12px;
    height: 12px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .discover-page {
    scroll-behavior: auto;
  }
  .destination-card,
  .destination-photo > img,
  .shortcut-icon {
    transition: none;
  }
}

.hero-type {
  position: absolute;
  right: 22px;
  top: 21px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border: 1px solid #ffffff7a;
  border-radius: 20px;
  color: #4e675e;
  background: #ffffffe0;
  font-size: 10px;
  backdrop-filter: blur(10px);
}
.discover-shortcuts small {
  font-size: 11px;
}
.discover-section-heading > div > p:last-child {
  font-size: 13px;
}
.destination-description {
  font-size: 12px;
}
.destination-tags > span {
  font-size: 10px;
}
.mood-filters > button {
  font-size: 12px;
}
.companion-description {
  font-size: 13px;
}
.companion-prompts > button {
  font-size: 12px;
}
.companion-note {
  font-size: 10px;
}
.map-invite-copy p,
.travel-map-invite > button {
  font-size: 12px;
}
.discover-footer,
.discover-footer a {
  font-size: 11px;
}
@media (max-width: 600px) {
  .hero-content h1 {
    font-size: 32px;
  }
  .hero-description {
    font-size: 13px;
    max-width: 260px;
  }
  .discover-hero {
    min-height: 355px;
  }
  .discovery-search input {
    font-size: 14px;
  }
  .hero-suggestions button,
  .hero-suggestions > span {
    font-size: 10px;
    min-height: 25px;
  }
  .hero-suggestions {
    gap: 6px;
  }
  .hero-type {
    right: 15px;
    top: 20px;
    font-size: 8px;
    gap: 4px;
    padding: 6px 8px;
  }
  .hero-type > svg {
    width: 11px;
    height: 11px;
  }
  .hero-location {
    font-size: 10px;
    bottom: 12px;
  }
  .discover-shortcuts strong {
    font-size: 11px;
  }
  .discover-section-heading > div > p:last-child {
    font-size: 12px;
  }
  .destination-title > span {
    font-size: 13px;
  }
  .destination-description {
    font-size: 12px;
  }
  .destination-tags > span {
    font-size: 10px;
  }
  .mood-filters > button {
    font-size: 11px;
    min-height: 40px;
  }
  .more-destinations {
    min-width: 40px;
    height: 40px;
  }
  .map-invite-copy p,
  .travel-map-invite > button {
    font-size: 11px;
  }
  .companion-description {
    font-size: 12px;
  }
  .companion-note {
    font-size: 9px;
  }
  .discover-footer,
  .discover-footer a {
    font-size: 10px;
  }
  .discover-footer p {
    max-width: 205px;
  }
  .discovery-companion h2 {
    font-size: 19px;
  }
  .companion-start {
    min-height: 44px;
  }
}

.hero-description,
.discover-section-heading > div > p:last-child,
.destination-description {
  color: #6c786f;
}
.discover-shortcuts small {
  color: #7e8a7f;
}
.mood-filters > button {
  color: #707d70;
}
.destination-title > span {
  color: #687761;
}
.destination-tags > span {
  color: #66745c;
}
.map-invite-copy p {
  color: #6b7e5d;
}
.companion-description {
  color: #81765f;
}
.companion-note {
  color: #86795b;
}
.discover-footer,
.discover-footer a {
  color: #76836e;
}
.hero-suggestions button {
  color: #5e7265;
}
.discovery-search input::placeholder {
  color: #77847a;
}

.discover-hero--immersive .hero-light {
  background:
    linear-gradient(90deg, #102c38b8 0%, #173a4866 42%, #173a4800 80%),
    linear-gradient(0deg, #132b3647, transparent 65%);
}
.discover-hero--immersive .hero-content h1 {
  color: #fffdf6;
  text-shadow: 0 2px 16px #172e3e26;
}
.discover-hero--immersive .hero-content h1 > span {
  color: #ffb494;
}
.discover-hero--immersive .hero-description {
  color: #f4f8f2;
}
.discover-hero--immersive .hero-kicker {
  color: #eff5f0;
}
.discover-hero--immersive .hero-kicker > span {
  background: #ffb494;
}
.discover-hero--immersive .hero-suggestions,
.discover-hero--immersive .hero-suggestions > span,
.discover-hero--immersive .hero-suggestions button {
  color: #f7fbf2;
}
.discover-hero--immersive .hero-suggestions i {
  background: #e4eee6;
}
@media (max-width: 600px) {
  .discover-hero--immersive .hero-light {
    background:
      linear-gradient(90deg, #122c39ba, #193c4666 65%, #1b3b453b),
      linear-gradient(0deg, #16323e55, transparent 70%);
  }
  .discover-hero--immersive .hero-location {
    color: #f3faf2;
  }
  .discover-hero--immersive .hero-location i {
    background: #daeadd;
  }
}
</style>
