<script setup lang="ts">
import AMapLoader from '@amap/amap-jsapi-loader'
import { computed, nextTick, onBeforeUnmount, ref, useId, watch } from 'vue'
import type { AgentDay } from '../api/agent'

const props = withDefaults(
  defineProps<{
    days: AgentDay[]
    activeDay: number
    allowExternal: boolean
    selectedStopId?: string | null
    compact?: boolean
  }>(),
  { selectedStopId: null, compact: false },
)
const emit = defineEmits<{ select: [point: { day: number; candidateId: string }] }>()
const host = ref<HTMLDivElement | null>(null)
const live = ref(false)
const mapError = ref('')
const gridId = `route-grid-${useId()}`
let map: AMap.Map | null = null
let version = 0
let markers: Array<{
  marker: AMap.Marker
  label: HTMLButtonElement
  day: number
  id: string
  color: string
}> = []
let paths: Array<{ path: AMap.Polyline; day: number }> = []
const palette = ['#ce4b29', '#56816a', '#a8873a', '#77779a']
const stops = computed(() =>
  props.days.flatMap((d) => d.stops.map((s, index) => ({ ...s, day: d.day, index: index + 1 }))),
)
const selected = (day: number, id: string) => day === props.activeDay && id === props.selectedStopId
const markerLabel = (day: number, index: number, name: string) =>
  `地图地点：第${day}天第${index}站 ${name}`
const layout = computed(() => {
  const all = stops.value
  if (!all.length) return []
  const minX = Math.min(...all.map((s) => s.longitude)),
    maxX = Math.max(...all.map((s) => s.longitude))
  const minY = Math.min(...all.map((s) => s.latitude)),
    maxY = Math.max(...all.map((s) => s.latitude))
  return all.map((s) => ({
    ...s,
    x:
      maxX === minX
        ? props.compact
          ? 180
          : 270
        : (props.compact ? 45 : 65) +
          ((s.longitude - minX) / (maxX - minX)) * (props.compact ? 270 : 410),
    y: maxY === minY ? 150 : 245 - ((s.latitude - minY) / (maxY - minY)) * 190,
  }))
})
function line(day: number) {
  return layout.value
    .filter((s) => s.day === day)
    .map((s) => `${s.x},${s.y}`)
    .join(' ')
}
function selectStop(day: number, candidateId: string) {
  emit('select', { day, candidateId })
}
function syncLiveMap(fit: boolean) {
  if (!map) return
  for (const item of markers) {
    const isSelected = selected(item.day, item.id)
    item.label.style.opacity = item.day === props.activeDay ? '1' : '0.4'
    item.label.style.outline = isSelected ? `3px solid ${item.color}` : ''
    item.label.style.outlineOffset = '3px'
    item.label.setAttribute('aria-pressed', String(isSelected))
  }
  for (const item of paths)
    item.path.setOptions({ strokeOpacity: item.day === props.activeDay ? 1 : 0.2 })
  if (fit) {
    const dayMarkers = markers.filter((m) => m.day === props.activeDay).map((m) => m.marker)
    if (dayMarkers.length) map.setFitView(dayMarkers, true, [35, 35, 35, 35], 16)
  }
}
async function drawMap() {
  const current = ++version
  map?.destroy()
  map = null
  markers = []
  paths = []
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
    const first = stops.value.find((s) => s.day === props.activeDay) ?? stops.value[0]!
    map = new A.Map(host.value, { zoom: 12, center: [first.longitude, first.latitude] })
    for (const day of props.days) {
      const color = palette[(day.day - 1) % palette.length]!
      if (day.stops.length > 1) {
        const path = new A.Polyline({
          path: day.stops.map((s) => [s.longitude, s.latitude]),
          strokeColor: color,
          strokeWeight: 3,
          strokeStyle: 'dashed',
        })
        paths.push({ path, day: day.day })
        map.add(path)
      }
      day.stops.forEach((s, index) => {
        const label = document.createElement('button')
        label.type = 'button'
        label.textContent = `${day.day}.${index + 1}`
        label.setAttribute('aria-label', markerLabel(day.day, index + 1, s.name))
        Object.assign(label.style, {
          background: color,
          color: '#fffdf7',
          border: '2px solid #fffdf7',
          padding: '6px 8px',
          borderRadius: '50%',
          fontSize: '11px',
          fontWeight: '600',
          cursor: 'pointer',
          boxShadow: '0 2px 8px #263e3026',
        })
        label.addEventListener('click', (event) => {
          event.stopPropagation()
          selectStop(day.day, s.candidate_id)
        })
        const marker = new A.Marker({
          position: [s.longitude, s.latitude],
          title: s.name,
          content: label,
        })
        markers.push({ marker, label, day: day.day, id: s.candidate_id, color })
        map!.add(marker)
      })
    }
    syncLiveMap(true)
    live.value = true
  } catch {
    if (current !== version) return
    map?.destroy()
    map = null
    markers = []
    paths = []
    mapError.value = '底图暂时不可用，已显示地点示意。'
  }
}
watch(() => [props.days, props.allowExternal, props.compact], drawMap, { immediate: true })
watch(
  () => props.activeDay,
  () => syncLiveMap(true),
)
watch(
  () => props.selectedStopId,
  () => syncLiveMap(false),
)
onBeforeUnmount(() => {
  version++
  map?.destroy()
  map = null
  markers = []
  paths = []
})
</script>

<template>
  <figure class="agent-map" :class="{ compact }" aria-label="行程地点地图">
    <div class="map-stage">
      <div ref="host" class="live-map" :class="{ visible: live }"></div>
      <svg
        v-if="!live"
        :viewBox="`0 0 ${compact ? 360 : 540} 300`"
        role="group"
        aria-label="GCJ-02地点坐标示意，连线只表示游览顺序"
      >
        <defs>
          <pattern :id="gridId" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M30 0H0V30" fill="none" stroke="#c2d0bd" stroke-width=".7" />
          </pattern>
        </defs>
        <rect :width="compact ? 360 : 540" height="300" fill="#edf2e7" />
        <rect :width="compact ? 360 : 540" height="300" :fill="`url(#${gridId})`" />
        <g v-for="day in days" :key="day.day" :opacity="day.day === activeDay ? 1 : 0.35">
          <polyline
            :points="line(day.day)"
            fill="none"
            :stroke="palette[(day.day - 1) % palette.length]"
            stroke-width="2"
            stroke-dasharray="5 6"
          />
          <g
            v-for="point in layout.filter((p) => p.day === day.day)"
            :key="point.candidate_id"
            class="map-marker"
            :class="{ selected: selected(point.day, point.candidate_id) }"
            role="button"
            tabindex="0"
            :aria-label="markerLabel(point.day, point.index, point.name)"
            :aria-pressed="selected(point.day, point.candidate_id)"
            @click="selectStop(point.day, point.candidate_id)"
            @keydown.enter.prevent="selectStop(point.day, point.candidate_id)"
            @keydown.space.prevent="selectStop(point.day, point.candidate_id)"
          >
            <title>{{ point.name }}</title>
            <circle :cx="point.x" :cy="point.y" r="29" fill="transparent" />
            <circle
              class="marker-focus-ring"
              :cx="point.x"
              :cy="point.y"
              r="23"
              fill="none"
              :stroke="palette[(day.day - 1) % palette.length]"
              stroke-width="2"
            />
            <circle
              :cx="point.x"
              :cy="point.y"
              r="16"
              :fill="
                selected(point.day, point.candidate_id)
                  ? palette[(day.day - 1) % palette.length]
                  : '#fffef7'
              "
              :stroke="palette[(day.day - 1) % palette.length]"
              stroke-width="2"
            />
            <text
              :x="point.x"
              :y="point.y + 4"
              text-anchor="middle"
              font-size="11"
              font-weight="650"
              :fill="
                selected(point.day, point.candidate_id)
                  ? '#fffef7'
                  : palette[(day.day - 1) % palette.length]
              "
            >
              {{ point.day }}.{{ point.index }}
            </text>
          </g>
        </g>
        <text :x="compact ? 326 : 501" y="28" font-size="11" fill="#73856a">N ↑</text>
      </svg>
    </div>
    <figcaption>
      <span>{{ live ? '高德地图' : '地点坐标示意 · 非导航底图' }}</span
      ><small>{{ mapError || '连线仅表示游览顺序，实际道路以导航为准' }}</small>
    </figcaption>
  </figure>
</template>

<style scoped>
.agent-map {
  position: relative;
  overflow: hidden;
  margin: 0;
  border: 1px solid #d9e3d1;
  border-radius: var(--radius-surface);
  background: #edf2e7;
}
.map-stage {
  position: relative;
  height: clamp(230px, 26vw, 330px);
}
.compact .map-stage {
  height: 235px;
}
.map-stage > svg {
  display: block;
  width: 100%;
  height: 100%;
}
.live-map {
  position: absolute;
  inset: 0;
  opacity: 0;
  pointer-events: none;
}
.live-map.visible {
  opacity: 1;
  pointer-events: auto;
}
.map-marker {
  cursor: pointer;
  outline: none;
}
.marker-focus-ring {
  opacity: 0;
}
.map-marker.selected .marker-focus-ring,
.map-marker:focus-visible .marker-focus-ring {
  opacity: 1;
}
.map-marker:focus-visible .marker-focus-ring {
  stroke-width: 3;
}
figcaption {
  position: relative;
  display: flex;
  gap: 6px;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 10px 12px;
  background: #f7f9f1;
  color: var(--text-secondary);
  font-size: var(--font-label);
  line-height: 1.7;
}
figcaption small {
  font-size: var(--font-label);
  color: var(--text-secondary);
}
.compact figcaption {
  flex-direction: column;
  align-items: flex-start;
  font-size: var(--font-label);
  padding: 10px;
}
.compact figcaption small {
  font-size: var(--font-label);
  line-height: 1.8;
}
@media (max-width: 600px) {
  .map-stage {
    height: 230px;
  }
  figcaption {
    font-size: var(--font-label);
    padding: 9px 10px;
  }
  figcaption small {
    font-size: var(--font-label);
  }
}
</style>
