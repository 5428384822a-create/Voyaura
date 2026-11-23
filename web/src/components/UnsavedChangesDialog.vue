<script setup lang="ts">
import { ref } from 'vue'
import { ArrowLeft, FilePenLine } from 'lucide-vue-next'
import { useDialogFocus } from './useDialogFocus'
const emit = defineEmits<{ stay: []; discard: [] }>()
const dialog = ref<HTMLElement | null>(null)
useDialogFocus(dialog, () => emit('stay'), { initial: '[data-stay]' })
</script>
<template>
  <div class="unsaved-backdrop" @click.self="emit('stay')">
    <section
      ref="dialog"
      class="unsaved-dialog"
      role="dialog"
      aria-modal="true"
      aria-labelledby="unsaved-title"
    >
      <span class="unsaved-symbol"><FilePenLine :size="28" /></span>
      <p class="journey-kicker">KEEP YOUR WORDS CLOSE</p>
      <h2 id="unsaved-title">还有未保存的编辑。</h2>
      <p>
        当前页面的输入或修改尚未提交。现在离开，会放弃这些编辑；已经保存的档案仍会保留。
      </p>
      <div>
        <button
          data-stay
          type="button"
          class="journey-primary"
          @click="emit('stay')"
        >
          <ArrowLeft :size="16" />继续编辑</button
        ><button
          type="button"
          class="journey-secondary"
          @click="emit('discard')"
        >
          放弃编辑并离开
        </button>
      </div>
    </section>
  </div>
</template>
<style scoped>
.unsaved-backdrop {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: grid;
  place-items: center;
  padding: 20px;
  background: #293d326e;
  backdrop-filter: blur(5px);
}
.unsaved-dialog {
  width: min(460px, 100%);
  padding: 34px;
  border: 1px solid #e5dcc6;
  border-radius: 15px;
  background: #fffdf6;
  box-shadow: 0 25px 80px #172b2530;
  color: #566a46;
}
.unsaved-symbol {
  display: grid;
  place-items: center;
  width: 57px;
  height: 57px;
  border: 1px solid #e8d9bb;
  border-radius: 13px;
  color: #b08a52;
  background: #fbf2df;
  margin-bottom: 23px;
}
.unsaved-dialog .journey-kicker {
  font-size: 8px;
  color: #927e58;
}
.unsaved-dialog h2 {
  font-size: 24px;
  font-weight: 500;
  line-height: 1.6;
  margin: 10px 0 14px;
}
.unsaved-dialog > p:not(.journey-kicker) {
  font-size: 13px;
  line-height: 2;
  color: #74815f;
  margin: 0 0 25px;
}
.unsaved-dialog > div {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.unsaved-dialog button {
  font-size: 12px;
}
.unsaved-dialog .journey-secondary {
  color: #916843;
  border-color: #e1d3bb;
}
@media (max-width: 580px) {
  .unsaved-dialog {
    padding: 26px;
  }
  .unsaved-dialog h2 {
    font-size: 22px;
  }
  .unsaved-dialog > p:not(.journey-kicker) {
    font-size: 12px;
  }
  .unsaved-dialog > div {
    flex-direction: column;
  }
  .unsaved-dialog button {
    width: 100%;
  }
}
</style>
