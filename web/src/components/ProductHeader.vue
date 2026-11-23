<script setup lang="ts">
import { Sun, UserRound, ChevronDown } from 'lucide-vue-next'
import BrandLogo from './BrandLogo.vue'
import AppNavigation from './AppNavigation.vue'
import type { AppView } from '../types'
defineProps<{ activeView: AppView; connected: boolean }>()
const emit = defineEmits<{ select: [view: AppView]; connect: []; xiaoxi: [] }>()
</script>
<template>
  <header class="product-header">
    <div class="product-header__inner">
      <button
        type="button"
        class="product-brand"
        aria-label="Voyaura 发现首页"
        @click="emit('select', 'discover')"
      >
        <BrandLogo />
      </button>
      <AppNavigation :active-view="activeView" @select="emit('select', $event)" />
      <div class="product-header__actions">
        <button class="header-xiaoxi" type="button" aria-label="和小曦一起" @click="emit('xiaoxi')">
          <Sun :size="18" /><span>和小曦一起</span></button
        ><span class="header-divider" aria-hidden="true"></span
        ><button
          class="header-account"
          type="button"
          aria-label="我的私人档案"
          @click="emit('connect')"
        >
          <span class="account-symbol"><UserRound :size="19" /></span
          ><span>{{ connected ? '我的档案' : '连接档案' }}</span
          ><ChevronDown :size="13" />
        </button>
      </div>
    </div>
  </header>
</template>
<style scoped>
.product-header {
  position: absolute;
  inset: 0 0 auto;
  z-index: 70;
  height: var(--product-header-height);
  border-bottom: 1px solid #ede9e3;
  background: rgba(255, 254, 251, 0.96);
  backdrop-filter: blur(16px);
}
.product-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 28px;
  width: min(1320px, calc(100% - 80px));
  height: 100%;
  margin: auto;
}
.product-brand {
  display: flex;
  align-items: center;
  flex: none;
  padding: 8px 0;
  border: 0;
  background: transparent;
  cursor: pointer;
}
.product-header__actions {
  display: flex;
  gap: 18px;
  align-items: center;
}
.header-xiaoxi,
.header-account {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  border: 0;
  background: transparent;
  font-size: 13px;
  white-space: nowrap;
  cursor: pointer;
  color: #57645e;
}
.header-xiaoxi > svg {
  color: #ce8c28;
}
.header-divider {
  width: 1px;
  height: 20px;
  background: #e8e3da;
}
.account-symbol {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: #efece4;
  color: #67756a;
}
.header-account > svg {
  color: #989e98;
}
@media (min-width: 900px) and (max-width: 1100px) {
  .product-header__inner {
    width: calc(100% - 40px);
    gap: 10px;
  }
  .header-xiaoxi {
    display: none;
  }
  .header-divider {
    display: none;
  }
}
@media (max-width: 899px) {
  .product-header__inner {
    width: calc(100% - 40px);
    gap: 10px;
  }
  .product-header__actions {
    gap: 14px;
  }
  .header-divider,
  .header-xiaoxi > span,
  .header-account > span:not(.account-symbol),
  .header-account > svg {
    display: none;
  }
  .header-xiaoxi {
    width: 34px;
    justify-content: center;
  }
  .header-xiaoxi > svg {
    width: 21px;
    height: 21px;
  }
  .account-symbol {
    width: 32px;
    height: 32px;
  }
}
</style>
