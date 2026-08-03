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
  position: fixed; inset: 0; z-index: 100;
  background: rgba(28, 20, 8, .42);
  display: grid; place-items: center; padding: 20px;
}
.modal-box {
  width: 100%; max-width: 380px; max-height: 90vh; overflow: auto;
  background: var(--surface); border-radius: var(--radius); box-shadow: var(--shadow-md);
  border: 1px solid var(--border);
}
.modal-head {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 16px 18px; border-bottom: 1px solid var(--border);
}
.modal-head h3 { margin: 0; font-size: 15.5px; }
.modal-close {
  flex: none; width: 28px; height: 28px; padding: 0; border: none; background: none;
  color: var(--muted); display: grid; place-items: center; border-radius: 7px;
}
.modal-close:hover { background: var(--surface-2); color: var(--text); }
.modal-body { padding: 18px; }
</style>
