<template>
  <Modal :open="open" :title="title" size="sm" @close="!busy && $emit('cancel')">
    <template #icon>
      <span class="confirm-icon" :class="tone" aria-hidden="true">
        <component :is="tone === 'ok' ? CircleCheck : TriangleAlert" :size="18" />
      </span>
    </template>
    <p style="font-size:.875rem;color:var(--text)"><slot>{{ message }}</slot></p>
    <template #footer>
      <button type="button" class="btn" :disabled="busy" @click="$emit('cancel')">Cancel</button>
      <button
        type="button" class="btn" :class="tone === 'danger' ? 'btn-danger' : 'btn-primary'"
        :disabled="busy" @click="$emit('confirm')"
      >{{ busy ? 'Working…' : confirmLabel }}</button>
    </template>
  </Modal>
</template>

<script setup>
import { CircleCheck, TriangleAlert } from 'lucide-vue-next'
import Modal from './Modal.vue'
defineProps({
  open: Boolean, title: String, message: String, busy: Boolean,
  confirmLabel: { type: String, default: 'Confirm' },
  tone: { type: String, default: 'danger' }, // danger | warn | ok
})
defineEmits(['confirm', 'cancel'])
</script>
