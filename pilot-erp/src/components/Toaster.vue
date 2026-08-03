<template>
  <div class="toaster" aria-live="polite">
    <transition-group name="toast">
      <div v-for="t in toasts" :key="t.id" class="toast" :class="t.type" @click="dismiss(t.id)">
        <component :is="icon(t.type)" :size="18" :stroke-width="2.25" class="toast-ic" />
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
  position: fixed; z-index: 9999; left: 50%; bottom: 22px; transform: translateX(-50%);
  display: flex; flex-direction: column; gap: 10px; align-items: center;
  width: min(92vw, 400px); pointer-events: none;
}
.toast {
  pointer-events: auto; cursor: pointer; width: 100%;
  display: flex; align-items: center; gap: 10px; padding: 12px 15px;
  border-radius: 12px; background: var(--surface); color: var(--text);
  border: 1px solid var(--border); box-shadow: 0 12px 34px rgba(15, 27, 46, .18);
  font-size: 14px; font-weight: 600;
}
.toast-ic { flex: none; }
.toast.success .toast-ic { color: var(--green); }
.toast.error   .toast-ic { color: var(--red); }
.toast.info    .toast-ic { color: var(--brand); }
.toast-msg { flex: 1; }
.toast-enter-active, .toast-leave-active { transition: all .28s var(--ease, cubic-bezier(.4,0,.2,1)); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateY(12px) scale(.96); }
.toast-move { transition: transform .28s var(--ease, cubic-bezier(.4,0,.2,1)); }
</style>
