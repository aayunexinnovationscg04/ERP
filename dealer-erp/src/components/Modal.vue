<template>
  <Teleport to="body">
    <div class="modal-backdrop" @click.self="$emit('close')" @keydown.esc="$emit('close')">
      <div class="modal-box" role="dialog" aria-modal="true" :aria-label="title">
        <div class="modal-head">
          <h3>{{ title }}</h3>
          <button type="button" class="modal-close" @click="$emit('close')" aria-label="Close">
            <X :size="18" />
          </button>
        </div>
        <div class="modal-body"><slot /></div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { X } from 'lucide-vue-next'

defineProps({ title: String })
const emit = defineEmits(['close'])

function onKey(e) { if (e.key === 'Escape') emit('close') }
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0; z-index: 300;
  background: rgba(7, 21, 36, .6);
  display: grid; place-items: center; padding: 20px;
}
.modal-box {
  width: 100%; max-width: 420px; max-height: 90vh; overflow: auto;
  background: var(--surface); border-radius: var(--radius); box-shadow: var(--shadow-lg);
  border: 1px solid var(--border);
}
.modal-head {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 14px 14px 14px 20px; border-bottom: 1px solid var(--border);
}
.modal-head h3 { margin: 0; font-size: 16px; font-weight: 800; color: var(--ink-strong); }
.modal-close {
  flex: none; width: 36px; height: 36px; min-height: 36px; padding: 0; border: none; background: none;
  color: var(--muted); border-radius: var(--radius-sm);
}
.modal-close:hover { background: var(--surface-3); color: var(--text); }
.modal-body { padding: 18px 20px 20px; }

/* phones: bottom sheet */
@media (max-width: 600px) {
  .modal-backdrop { place-items: end stretch; padding: 0; }
  .modal-box { max-width: none; border-radius: 14px 14px 0 0; border-bottom: none; padding-bottom: env(safe-area-inset-bottom); }
  .modal-close { width: 44px; height: 44px; }
}
</style>
