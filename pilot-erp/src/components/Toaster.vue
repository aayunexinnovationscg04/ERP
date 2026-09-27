<template>
  <div class="toaster" aria-live="polite">
    <transition-group name="toast">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type" role="status" @click="dismiss(t.id)">
        <component :is="icon(t.type)" :size="20" :stroke-width="2.25" class="toast-ic" />
        <span class="toast-msg">{{ t.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { CircleCheck, CircleAlert, Info } from 'lucide-vue-next'
import { toasts, dismiss } from '../toast'
const icon = (t) => (t === 'success' ? CircleCheck : t === 'error' ? CircleAlert : Info)
</script>

<style scoped>
.toaster {
  position: fixed; z-index: 9999; left: 50%; transform: translateX(-50%);
  bottom: 24px; width: min(calc(100vw - 32px), 420px);
  display: flex; flex-direction: column; gap: 10px; align-items: stretch; pointer-events: none;
}
/* phones: sit just above the bottom tab bar */
@media (max-width: 767.98px) {
  .toaster { bottom: calc(var(--tabbar-h) + env(safe-area-inset-bottom, 0px) + 12px); }
}
.toast {
  pointer-events: auto; cursor: pointer;
  display: flex; align-items: center; gap: 12px; min-height: 52px; padding: 12px 16px;
  border-radius: var(--radius); background: var(--surface); color: var(--text);
  border: 1px solid var(--border-strong); border-left-width: 4px; box-shadow: var(--shadow-lg);
  font-size: .9375rem; font-weight: 600;
}
.toast.success { border-left-color: var(--green); }
.toast.error { border-left-color: var(--red); }
.toast.info { border-left-color: var(--info); }
.toast-ic { flex: none; }
.toast.success .toast-ic { color: var(--green); }
.toast.error .toast-ic { color: var(--red); }
.toast.info .toast-ic { color: var(--info); }
.toast-msg { flex: 1; }
.toast-enter-active, .toast-leave-active { transition: opacity .22s var(--ease), transform .22s var(--ease); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(10px); }
.toast-move { transition: transform .22s var(--ease); }
</style>
