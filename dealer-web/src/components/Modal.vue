<!-- Dialog in the admin console's style: title (+ optional one-line
     description), body, and an optional footer bar for the actions.
     Phones get a bottom sheet with full-width footer buttons. -->
<template>
  <Teleport to="body">
    <div class="modal-root">
      <div class="modal-scrim" @click="$emit('close')"></div>
      <div ref="panel" class="modal" role="dialog" aria-modal="true" :aria-labelledby="titleId" tabindex="-1">
        <div class="modal-head">
          <div style="min-width:0">
            <h2 :id="titleId">{{ title }}</h2>
            <p v-if="description">{{ description }}</p>
          </div>
          <button type="button" class="modal-close" @click="$emit('close')" aria-label="Close dialog">
            <X :size="18" />
          </button>
        </div>
        <div class="modal-body"><slot /></div>
        <div v-if="$slots.footer" class="modal-foot"><slot name="footer" /></div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { nextTick, onMounted, onBeforeUnmount, ref } from 'vue'
import { X } from 'lucide-vue-next'

defineProps({ title: String, description: String })
const emit = defineEmits(['close'])
const panel = ref(null)
const titleId = 'm' + Math.random().toString(36).slice(2, 8)
let lastFocus = null

function onKey(e) { if (e.key === 'Escape') emit('close') }
onMounted(async () => {
  lastFocus = document.activeElement
  document.body.style.overflow = 'hidden'
  window.addEventListener('keydown', onKey)
  await nextTick()
  const first = panel.value?.querySelector('input, select, textarea')
  ;(first || panel.value)?.focus({ preventScroll: true })
})
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
  lastFocus?.focus?.({ preventScroll: true })
})
</script>

<style scoped>
.modal-root { position: fixed; inset: 0; z-index: 300; display: flex; align-items: center; justify-content: center; padding: 20px; }
.modal-scrim { position: absolute; inset: 0; background: rgba(7, 21, 36, .55); }
.modal {
  position: relative; width: 100%; max-width: 420px; max-height: calc(100dvh - 40px);
  display: flex; flex-direction: column; outline: none;
  background: var(--surface); border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow-lg);
}
.modal-head { display: flex; align-items: flex-start; gap: 12px; padding: 18px 20px 14px; border-bottom: 1px solid var(--border); }
.modal-head h2 { font-size: 1.05rem; font-weight: 800; color: var(--ink-strong); }
.modal-head p { font-size: .8125rem; color: var(--muted); margin-top: 3px; }
.modal .modal-close {
  flex: none; width: 38px; height: 38px; min-height: 0; padding: 0; margin: -6px -8px 0 auto;
  border: 1px solid transparent; background: transparent; color: var(--muted); box-shadow: none;
}
.modal .modal-close:hover { background: var(--surface-3); color: var(--text); }
.modal-body { padding: 18px 20px; overflow-y: auto; }
.modal-foot {
  display: flex; justify-content: flex-end; gap: 10px; padding: 14px 20px;
  border-top: 1px solid var(--border); background: var(--surface-2); border-radius: 0 0 12px 12px;
}

@media (max-width: 720px) {
  .modal-root { align-items: flex-end; padding: 0; }
  .modal { max-width: none; border-radius: 14px 14px 0 0; max-height: 92dvh; border-bottom: 0; }
  .modal-foot { border-radius: 0; padding-bottom: calc(14px + env(safe-area-inset-bottom)); }
  .modal-foot :slotted(button) { flex: 1; }
  .modal .modal-close { width: 44px; height: 44px; }
}
</style>
