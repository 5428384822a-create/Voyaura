<script setup lang="ts">
import AMapLoader from '@amap/amap-jsapi-loader'
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import type { AgentDay } from '../api/agent'

const props = defineProps<{ days: AgentDay[]; activeDay: number; allowExternal: boolean }>()
const host = ref<HTMLDivElement | null>(null)
const live = ref(false)
const mapError = ref('')
let map: AMap.Map | null = null
let version = 0
const palette = ['#e9583e', '#4d7c6a', '#b8892e', '#6a69a1']
const stops = computed(() =>
  props.days.flatMap((d) => d.stops.map((s, index) => ({ ...s, day: d.day, index: index + 1 }))),
)
const layout = computed(() => {
  const all = stops.value
  if (!all.length) return []
  const minX = Math.min(...all.map((s) => s.longitude))
  const maxX = Math.max(...all.map((s) => s.longitude))
  const minY = Math.min(...all.map((s) => s.latitude))
  const maxY = Math.max(...all.map((s) => s.latitude))
  const spanX = maxX - minX || 0.01
  const spanY = maxY - minY || 0.01
  return all.map((s) => ({
    ...s,
    x: 65 + ((s.longitude - minX) / spanX) * 410,
    y: 245 - ((s.latitude - minY) / spanY) * 190,
  }))
})
function line(day: number) {
  return layout.value
    .filter((s) => s.day === day)
    .map((s) => `${s.x},${s.y}`)
    .join(' ')
}
async function drawMap() {
  const current = ++version
  map?.destroy()
  map = null
  live.value = false
  mapError.value = ''
  if (!props.allowExternal || !import.meta.env.VITE_AMAP_KEY || !stops.value.length) return
  await nextTick()
  try {
    window._AMapSecurityConfig = { securityJsCode: import.meta.env.VITE_AMAP_SECURITY_CODE ?? '' }
    const A = (await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_KEY,
      version: '2.0',
    })) as typeof AMap
    if (current !== version || !host.value) return
    map = new A.Map(host.value, {
      zoom: 12,
      center: [stops.value[0]!.longitude, stops.value[0]!.latitude],
    })
    props.days.forEach((day) => {
      const color = palette[(day.day - 1) % palette.length]
      if (day.stops.length > 1)
        map!.add(
          new A.Polyline({
            path: day.stops.map((s) => [s.longitude, s.latitude]),
            strokeColor: color,
            strokeWeight: 4,
            strokeStyle: 'dashed',
          }),
        )
      day.stops.forEach((s, i) => {
        const label = document.createElement('span')
        label.textContent = `${day.day}.${i + 1}`
        Object.assign(label.style, {
          background: color,
          color: '#fff',
          padding: '4px 7px',
          borderRadius: '12px',
          fontSize: '12px',
        })
        map!.add(
          new A.Marker({ position: [s.longitude, s.latitude], title: s.name, content: label }),
        )
      })
    })
    map.setFitView()
    live.value = true
  } catch {
    mapError.value = '底图暂时不可用，已显示地点示意。'
  }
}
watch(() => [props.days, props.allowExternal], drawMap, { immediate: true })
onBeforeUnmount(() => {
  version++
  map?.destroy()
})
</script>

<template>
  <figure class="agent-map" aria-label="行程地点地图">
    <div ref="host" class="live-map" :class="{ visible: live }"></div>
    <svg
      v-if="!live"
      viewBox="0 0 540 300"
      role="img"
      aria-label="GCJ-02地点坐标示意，连线只表示游览顺序"
    >
      <defs>
        <pattern id="travel-grid" width="30" height="30" patternUnits="userSpaceOnUse">
          <path d="M30 0H0V30" fill="none" stroke="#b8c8b8" stroke-width=".6" />
        </pattern>
      </defs>
      <rect width="540" height="300" fill="#e5ebdf" />
      <rect width="540" height="300" fill="url(#travel-grid)" />
      <path
        d="M-25 260Q170 100 260 310M320-20Q220 100 570 190"
        stroke="#d5dfd0"
        stroke-width="35"
        fill="none"
      />
      <g v-for="day in days" :key="day.day" :opacity="day.day === activeDay ? 1 : 0.35">
        <polyline
          :points="line(day.day)"
          fill="none"
          :stroke="palette[(day.day - 1) % palette.length]"
          stroke-width="2.5"
          stroke-dasharray="6 5"
        />
        <g v-for="point in layout.filter((p) => p.day === day.day)" :key="point.candidate_id">
          <circle
            :cx="point.x"
            :cy="point.y"
            r="15"
            fill="#fffdf7"
            :stroke="palette[(day.day - 1) % palette.length]"
            stroke-width="2"
          />
          <text
            :x="point.x"
            :y="point.y + 4"
            text-anchor="middle"
            font-size="11"
            font-weight="700"
            :fill="palette[(day.day - 1) % palette.length]"
          >
            {{ point.day }}.{{ point.index }}
          </text>
        </g>
      </g>
      <text x="20" y="28" font-size="10" fill="#687a68" letter-spacing="2">
        VOYAURA · JOURNEY ATLAS
      </text>
      <text x="506" y="32" font-size="12" fill="#687a68">N ↑</text>
    </svg>
    <figcaption>
      <span>{{ live ? '高德地图' : '地点坐标示意 · 非导航底图' }}</span
      ><small>{{ mapError || '虚线表示游览顺序，实际道路以导航为准' }}</small>
    </figcaption>
  </figure>
</template>

<style scoped>
.agent-map {
  position: relative;
  min-height: 250px;
  overflow: hidden;
  margin: 0;
  border: 1px solid #cbd6c5;
  border-radius: 12px;
  background: #e5ebdf;
}
.agent-map svg {
  display: block;
  width: 100%;
  max-height: 330px;
}
.live-map {
  position: absolute;
  inset: 0 0 35px;
  opacity: 0;
  pointer-events: none;
}
.live-map.visible {
  opacity: 1;
  pointer-events: auto;
}
figcaption {
  position: relative;
  display: flex;
  gap: 8px;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 9px 12px;
  background: #f4f6ed;
  color: #5c6d59;
  font-size: 10px;
}
figcaption small {
  font-size: 9px;
}
</style>
