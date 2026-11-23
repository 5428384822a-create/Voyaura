<script setup lang="ts">
import { Check, LoaderCircle, CircleAlert } from 'lucide-vue-next'
import { computed } from 'vue'
const props = defineProps<{ phase: 'brief' | 'working' | 'review' | 'blocked' | 'saved' }>()
const steps = ['旅行想法', '整理草案', '核对细节', '私人收藏']
const current = computed(
  () => ({ brief: 0, working: 1, review: 2, blocked: 1, saved: 3 })[props.phase],
)
</script>
<template>
  <ol class="workflow-steps" aria-label="旅行规划进度">
    <li
      v-for="(step, index) in steps"
      :key="step"
      :class="{
        complete: index < current || phase === 'saved',
        current: index === current,
        blocked: index === current && phase === 'blocked',
      }"
      :aria-current="index === current ? 'step' : undefined"
    >
      <span class="step-symbol"
        ><CircleAlert v-if="index === current && phase === 'blocked'" :size="15" /><LoaderCircle
          v-else-if="index === current && phase === 'working'"
          class="spin"
          :size="15"
        /><Check v-else-if="index < current || phase === 'saved'" :size="14" /><span v-else>{{
          index + 1
        }}</span></span
      >
      <span>{{ step }}</span>
    </li>
  </ol>
</template>
<style scoped>
.workflow-steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  list-style: none;
  gap: 20px;
  margin: 0;
  padding: 0;
  color: #90958b;
  font-size: 12px;
}
.workflow-steps li {
  position: relative;
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 34px;
}
.workflow-steps li:not(:last-child)::after {
  content: '';
  height: 1px;
  background: #e8e6df;
  flex: 1;
  margin-left: 10px;
}
.step-symbol {
  flex: none;
  width: 27px;
  height: 27px;
  border: 1px solid #dfdfd5;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #fffefb;
  color: #979c91;
  font-size: 11px;
}
.complete {
  color: #6d8064;
}
.complete .step-symbol {
  background: #eef3e8;
  border-color: #d7e2cb;
  color: #647d56;
}
.current {
  color: var(--brand-ink-orange);
  font-weight: 600;
}
.current .step-symbol {
  color: var(--brand-ink-orange);
  background: #fff0e8;
  border-color: #efc4b0;
}
.blocked .step-symbol {
  background: #fff5df;
  color: #997a31;
  border-color: #e7d6a9;
}
.spin {
  animation: step-spin 1.4s linear infinite;
}
@keyframes step-spin {
  to {
    transform: rotate(360deg);
  }
}
@media (max-width: 600px) {
  .workflow-steps {
    gap: 7px;
    font-size: 10px;
  }
  .workflow-steps li {
    gap: 6px;
    white-space: nowrap;
  }
  .workflow-steps li:not(:last-child)::after {
    margin-left: 0;
  }
  .step-symbol {
    width: 23px;
    height: 23px;
    font-size: 10px;
  }
}
@media (prefers-reduced-motion: reduce) {
  .spin {
    animation: none;
  }
}
@media (max-width: 360px) {
  .workflow-steps li {
    flex-direction: column;
    gap: 5px;
    min-width: 0;
  }
  .workflow-steps li:not(:last-child)::after {
    position: absolute;
    top: 12px;
    right: -10px;
    width: 13px;
    margin: 0;
  }
}
</style>
