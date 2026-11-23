<script setup lang="ts">
defineProps<{ compact?: boolean }>()
</script>
<template>
  <span class="voyaura-logo" aria-label="Voyaura">
    <svg viewBox="0 0 46 27" fill="none" aria-hidden="true">
      <path
        d="M2 18.5 12.6 8.3c2.7-2.6 5.2-2.4 8 .2l2.5 2.2 3.4-4.1c2.8-3.5 5.8-3.4 8.8.1L44 18.3c-6.2 4.6-10.4 3.8-15.7-.7l-3.9-3.3-3.3 3.3c-6.8 6.5-11.8 6.4-19.1.9Z"
        fill="currentColor"
      />
      <path
        d="m12 15.7 3.1-3.1 3.4 3.1"
        stroke="white"
        stroke-width="1.7"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    <span v-if="!compact">Voyaura<span class="logo-dot">.</span></span>
  </span>
</template>
<style scoped>
.voyaura-logo {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--brand-orange, #ef643b);
  font-family: Arial, 'Microsoft YaHei', sans-serif;
  font-size: 27px;
  line-height: 1;
  font-weight: 750;
  letter-spacing: -1.2px;
}
.voyaura-logo svg {
  width: 39px;
  height: 27px;
  flex: none;
}
.logo-dot {
  color: var(--brand-orange, #ef643b);
}
@media (max-width: 600px) {
  .voyaura-logo {
    font-size: 25px;
    gap: 6px;
  }
  .voyaura-logo svg {
    width: 33px;
  }
}
</style>
