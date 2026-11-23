<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { KeyRound, LockKeyhole, X } from 'lucide-vue-next'
import { ApiClientError, request } from '../api/client'
import {
  clearSession,
  getAccessToken,
  setAccessToken,
  setOwnerUsername,
} from '../api/session'

const emit = defineEmits<{ connected: []; close: []; disconnected: [] }>()
defineProps<{ returnLabel?: string }>()
const token = ref('')
const busy = ref(false)
const error = ref('')
const input = ref<HTMLInputElement | null>(null)
const hadSession = Boolean(getAccessToken())
onMounted(() => input.value?.focus())
async function connect() {
  busy.value = true
  error.value = ''
  const previous = getAccessToken()
  setAccessToken(token.value)
  try {
    const actor = await request<{ username: string }>('/auth/me')
    setOwnerUsername(actor.username)
    token.value = ''
    emit('connected')
  } catch (e) {
    setAccessToken(previous)
    error.value =
      e instanceof ApiClientError ? e.message : '连接失败，请稍后重试。'
  } finally {
    busy.value = false
  }
}
function disconnect() {
  clearSession()
  emit('disconnected')
}
function trapFocus(event: KeyboardEvent) {
  if (event.key !== 'Tab') return
  const items = Array.from(
    (event.currentTarget as HTMLElement).querySelectorAll<HTMLElement>(
      'button:not(:disabled),input',
    ),
  )
  const first = items[0]
  const last = items.at(-1)
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault()
    last?.focus()
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault()
    first?.focus()
  }
}
</script>

<template>
  <div
    class="connection-backdrop"
    @keydown.esc="emit('close')"
    @keydown="trapFocus"
  >
    <section
      role="dialog"
      aria-modal="true"
      aria-labelledby="connection-title"
      class="connection-card"
    >
      <button
        class="connection-close"
        type="button"
        aria-label="关闭连接窗口"
        @click="emit('close')"
      >
        <X :size="20" />
      </button>
      <div class="connection-icon"><LockKeyhole :size="28" /></div>
      <p class="eyebrow">YOUR PRIVATE TRAVEL ARCHIVE</p>
      <h1 id="connection-title">连接你的私人旅程</h1>
      <p>输入本机服务提供的访问令牌，打开专属地图、行程和旅行记忆。</p>
      <p v-if="returnLabel" class="connection-return">
        验证后继续：{{ returnLabel }}
      </p>
      <form @submit.prevent="connect">
        <label for="access-token">访问令牌</label>
        <input
          id="access-token"
          ref="input"
          v-model="token"
          :disabled="busy"
          type="password"
          autocomplete="off"
          spellcheck="false"
          required
          minlength="32"
          placeholder="粘贴本机访问令牌"
        />
        <p v-if="error" class="connection-error" role="alert">{{ error }}</p>
        <button
          class="connection-submit"
          type="submit"
          :disabled="busy || token.trim().length < 32"
        >
          <KeyRound :size="17" />{{ busy ? '正在验证…' : '连接 Voyaura' }}
        </button>
      </form>
      <small
        >令牌仅保存在本标签页会话，断开后需重新输入。请勿与他人分享。</small
      >
      <button
        v-if="hadSession"
        class="disconnect"
        type="button"
        @click="disconnect"
      >
        断开并清除本页会话
      </button>
    </section>
  </div>
</template>

<style scoped>
.connection-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 20px;
  background: #25352d6e;
  backdrop-filter: blur(9px);
}
.connection-card {
  position: relative;
  width: min(440px, 100%);
  padding: 38px;
  border: 1px solid #d3c9b8;
  border-radius: 20px;
  background: var(--paper);
  box-shadow: 0 25px 90px #16261e38;
}
.connection-close {
  position: absolute;
  right: 15px;
  top: 15px;
  border: 0;
  background: transparent;
  cursor: pointer;
}
.connection-icon {
  width: 62px;
  height: 62px;
  display: grid;
  place-items: center;
  margin-bottom: 25px;
  border-radius: 18px;
  color: #53745b;
  background: #e2e9dd;
}
h1 {
  font-size: 25px;
  letter-spacing: -1px;
  margin: 10px 0;
}
p {
  font-size: 13px;
  line-height: 1.8;
  color: #6b736c;
}
label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  margin: 22px 0 8px;
}
input {
  width: 100%;
  padding: 12px;
  border: 1px solid #c9c5b8;
  border-radius: 8px;
  background: #fffdf7;
}
.connection-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin: 14px 0 18px;
  padding: 13px;
  border: 0;
  border-radius: 8px;
  color: white;
  background: var(--coral);
  cursor: pointer;
}
.connection-submit:disabled {
  opacity: 0.5;
  cursor: wait;
}
small {
  display: block;
  color: #777c74;
  font-size: 11px;
  line-height: 1.7;
}
.connection-error {
  color: #a33428;
}
.connection-return {
  margin: 16px 0 0;
  padding: 10px 12px;
  border: 1px solid #e6ddc8;
  border-radius: 7px;
  background: #faf3e3;
  color: #8b7047;
  font-size: 11px;
}
.disconnect {
  display: block;
  margin: 18px auto 0;
  padding: 7px;
  border: 0;
  background: transparent;
  color: #ac4934;
  font-size: 12px;
  cursor: pointer;
}
</style>
