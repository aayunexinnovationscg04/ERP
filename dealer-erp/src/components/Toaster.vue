<template>
  <div class="toaster" aria-live="polite">
    <transition-group name="toast">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type" @click="dismiss(t.id)">
        <component :is="icon(t.type)" :size="18" class="toast-ic" />
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
  position: fixed; z-index: 9999; right: 20px; bottom: 20px;
  display: flex; flex-direction: column; gap: 10px; align-items: stretch;
  width: min(calc(100vw - 32px), 380px); pointer-events: none;
}
.toast {
  pointer-events: auto; cursor: pointer; width: 100%;
  display: flex; align-items: center; gap: 10px; padding: 12px 14px;
  border-radius: var(--radius-sm); background: var(--surface); color: var(--text);
  border: 1px solid var(--border-strong); border-left-width: 4px; box-shadow: var(--shadow-lg);
  font-size: 13.5px; font-weight: 600;
}
.toast-ic { flex: none; }
.toast.success { border-left-color: var(--green); }
.toast.error { border-left-color: var(--red); }
.toast.info { border-left-color: var(--info); }
.toast.success .toast-ic { color: var(--green); }
.toast.error   .toast-ic { color: var(--red); }
.toast.info    .toast-ic { color: var(--info); }
.toast-msg { flex: 1; }
.toast-enter-active, .toast-leave-active { transition: opacity .2s var(--ease), transform .2s var(--ease); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(8px); }
.toast-move { transition: transform .2s var(--ease); }
@media (max-width: 600px) {
  .toaster { right: 16px; left: 16px; width: auto; bottom: 16px; }
}
</style>
