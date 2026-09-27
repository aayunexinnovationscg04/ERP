<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-root" @keydown.esc="close">
        <div class="modal-scrim" @click="close"></div>
        <div
          ref="panel" class="modal" :class="size" role="dialog" aria-modal="true"
          :aria-labelledby="titleId" tabindex="-1"
        >
          <div class="modal-head">
            <slot name="icon" />
            <div style="min-width:0">
              <h2 :id="titleId">{{ title }}</h2>
              <p v-if="description">{{ description }}</p>
            </div>
            <button type="button" class="tb-btn" aria-label="Close dialog" @click="close"><X :size="18" /></button>
          </div>
          <div class="modal-body"><slot /></div>
          <div v-if="$slots.footer" class="modal-foot"><slot name="footer" /></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({ open: Boolean, title: String, description: String, size: String })
const emit = defineEmits(['close'])
const panel = ref(null)
const titleId = 'm' + Math.random().toString(36).slice(2, 8)
let lastFocus = null

function close() { emit('close') }
function onKey(e) { if (e.key === 'Escape' && props.open) close() }

watch(() => props.open, async (v) => {
  if (v) {
    lastFocus = document.activeElement
    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', onKey)
    await nextTick()
    const first = panel.value?.querySelector('input, select, textarea')
    ;(first || panel.value)?.focus({ preventScroll: true })
  } else {
    document.body.style.overflow = ''
    window.removeEventListener('keydown', onKey)
    lastFocus?.focus?.({ preventScroll: true })
  }
})
onBeforeUnmount(() => { window.removeEventListener('keydown', onKey); document.body.style.overflow = '' })
</script>
