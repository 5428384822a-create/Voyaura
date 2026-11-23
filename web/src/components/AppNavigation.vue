<script setup lang="ts">
import { Compass, CalendarDays, Map, Aperture, UserRound } from 'lucide-vue-next'
import type { Component } from 'vue'
import type { AppView } from '../types'
const props = withDefaults(defineProps<{ activeView: AppView; mode?: 'desktop' | 'mobile' }>(), {
  mode: 'desktop',
})
const emit = defineEmits<{ select: [view: AppView] }>()
const items: Array<{ id: AppView; label: string; icon: Component }> = [
  { id: 'discover', label: '发现', icon: Compass },
  { id: 'journeys', label: '计划', icon: CalendarDays },
  { id: 'map', label: '旅程', icon: Map },
  { id: 'studio', label: '创作', icon: Aperture },
  { id: 'profile', label: '我的', icon: UserRound },
]
function selected(id: AppView) {
  return id === props.activeView || (id === 'map' && props.activeView === 'memories')
}
</script>
<template>
  <nav
    class="product-nav"
    :class="`product-nav--${mode}`"
    :aria-label="mode === 'desktop' ? '主要导航' : '手机主要导航'"
  >
    <button
      v-for="item in items"
      :key="item.id"
      class="product-nav__item"
      :class="{ selected: selected(item.id) }"
      :aria-current="selected(item.id) ? 'page' : undefined"
      type="button"
      @click="emit('select', item.id)"
    >
      <component :is="item.icon" :size="22" :stroke-width="1.7" /><span>{{ item.label }}</span>
    </button>
  </nav>
</template>
<style scoped>
.product-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 100%;
}
.product-nav__item {
  position: relative;
  min-width: 72px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 0 16px;
  border: 0;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--font-body);
  font-weight: 500;
  transition: color 0.18s;
}
.product-nav--desktop .product-nav__item > svg {
  display: none;
}
.product-nav__item:hover {
  color: var(--brand-orange);
}
.product-nav__item.selected {
  color: var(--brand-ink-orange);
  font-weight: 650;
}
.product-nav--desktop .product-nav__item.selected:after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 25%;
  right: 25%;
  height: 3px;
  background: var(--brand-orange);
  border-radius: 3px 3px 0 0;
}
.product-nav--mobile {
  display: none;
}
@media (max-width: 899px) {
  .product-nav--desktop {
    display: none;
  }
  .product-nav--mobile {
    position: absolute;
    inset: auto 0 0;
    height: calc(68px + env(safe-area-inset-bottom));
    z-index: 60;
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0;
    padding: 5px 10px max(5px, env(safe-area-inset-bottom));
    border-top: 1px solid #ece8e2;
    background: #fffefbf5;
    backdrop-filter: blur(18px);
  }
  .product-nav--mobile .product-nav__item {
    min-width: 0;
    flex-direction: column;
    gap: 4px;
    padding: 5px 0;
    border-radius: var(--radius-surface);
    font-size: var(--font-label);
    font-weight: 500;
  }
  .product-nav--mobile .product-nav__item.selected {
    color: var(--brand-ink-orange);
  }
  .product-nav--mobile .product-nav__item.selected > svg {
    stroke-width: 2.1;
  }
}
</style>
