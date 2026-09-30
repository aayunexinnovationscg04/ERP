<template>
  <div class="toaster" aria-live="polite">
    <transition-group name="toast">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type" role="status">
        <component :is="icon(t.type)" :size="18" class="toast-ic" />
        <span class="toast-msg">{{ t.message }}</span>
        <button type="button" class="toast-x" aria-label="Dismiss" @click="dismiss(t.id)"><X :size="15" /></button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { CircleCheck, CircleAlert, Info, X } from 'lucide-vue-next'
import { toasts, dismiss } from '../toast'
const icon = (t) => (t === 'success' ? CircleCheck : t === 'error' ? CircleAlert : Info)
</script>

<style scoped>
.toaster {
  position: fixed; z-index: 9999; right: 20px; bottom: 20px;
  display: flex; flex-direction: column; gap: 10px; align-items: flex-end;
  width: min(calc(100vw - 32px), 380px); pointer-events: none;
}
.toast {
  pointer-events: auto; width: 100%;
  display: flex; align-items: center; gap: 10px; padding: 12px 10px 12px 14px;
  border-radius: var(--radius); background: var(--surface); color: var(--text);
  border: 1px solid var(--border); border-left: 3px solid var(--info); box-shadow: var(--shadow-lg);
  font-size: .875rem; font-weight: 600;
}
.toast.success { border-left-color: var(--green); }
.toast.error { border-left-color: var(--red); }
.toast-ic { flex: none; color: var(--info); }
.toast.success .toast-ic { color: var(--green); }
.toast.error .toast-ic { color: var(--red); }
.toast-msg { flex: 1; min-width: 0; }
.toast-x {
  flex: none; width: 28px; height: 28px; border: 0; border-radius: var(--radius-xs);
  display: grid; place-items: center; background: transparent; color: var(--muted);
}
.toast-x:hover { background: var(--surface-3); color: var(--text); }
@media (max-width: 720px) { .toast-x { width: 40px; height: 40px; margin: -6px -6px -6px 0; } }
.toast-enter-active, .toast-leave-active { transition: all .22s var(--ease); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(10px); }
.toast-move { transition: transform .22s var(--ease); }
@media (max-width: 720px) {
  /* top on phones so toasts never cover a bottom sheet's action buttons */
  .toaster { left: 12px; right: 12px; top: calc(var(--topbar-h) + 8px); bottom: auto; width: auto; align-items: stretch; flex-direction: column-reverse; }
  .toast-enter-from, .toast-leave-to { transform: translateY(-10px); }
}
</style>
