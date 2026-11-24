<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next'
withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'tertiary' | 'destructive'
  type?: 'button' | 'submit' | 'reset'
  loading?: boolean
  disabled?: boolean
}>(), { variant: 'secondary', type: 'button', loading: false, disabled: false })
</script>
<template>
  <button :type="type" class="ui-button" :class="`ui-button--${variant}`" :disabled="disabled || loading" :aria-busy="loading || undefined"><LoaderCircle v-if="loading" class="spin" :size="18" aria-hidden="true" /><slot /></button>
</template>
