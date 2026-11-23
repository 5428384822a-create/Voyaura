<script setup lang="ts">
import { CircleCheck, CircleAlert, CircleX, Info } from 'lucide-vue-next'
withDefaults(defineProps<{ tone?: 'neutral' | 'success' | 'warning' | 'error' }>(), { tone: 'neutral' })
</script>
<template><span class="ui-status" :class="`ui-status--${tone}`"><component :is="tone === 'success' ? CircleCheck : tone === 'warning' ? CircleAlert : tone === 'error' ? CircleX : Info" :size="15" aria-hidden="true" /><slot /></span></template>
