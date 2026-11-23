<script setup lang="ts">
import { ArrowLeft, BookImage, Route, Sparkles, UserRound } from 'lucide-vue-next'
import { computed, type Component } from 'vue'
import type { AppView } from '../types'

const props = defineProps<{ view: Exclude<AppView, 'map' | 'discover'> }>()
const emit = defineEmits<{ back: [] }>()

const content = computed<Record<'title' | 'empty', string> & { icon: Component }>(() => {
  const pages = {
    journeys: { title: '行程', empty: '第一段行程会从这里出发', icon: Route },
    memories: {
      title: '记忆',
      empty: '第一张旅行底片正在等你',
      icon: BookImage,
    },
    studio: {
      title: '创作',
      empty: '把旅途变成你的视觉故事',
      icon: Sparkles,
    },
    profile: {
      title: '我的档案',
      empty: '从一段旅行开始，收好自己的回忆',
      icon: UserRound,
    },
  }
  return pages[props.view]
})
</script>

<template>
  <main class="empty-view">
    <header>
      <button type="button" title="返回地图" aria-label="返回地图" @click="emit('back')">
        <ArrowLeft />
      </button>
      <div>

        <h1>{{ content.title }}</h1>
      </div>
    </header>
    <section class="empty-state">
      <component :is="content.icon" :size="34" :stroke-width="1.5" />
      <p>{{ content.empty }}</p>
    </section>
  </main>
</template>
