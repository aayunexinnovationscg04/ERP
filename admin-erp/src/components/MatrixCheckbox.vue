<template>
  <button
    type="button" class="mcheck" :class="{ checked: modelValue }" :disabled="disabled"
    :style="colorStyle"
    role="checkbox" :aria-checked="modelValue" @click="toggle"
  >
    <AnimatePresence>
      <motion.span
        v-if="modelValue" class="tick"
        :initial="{ scale: 0, opacity: 0 }" :animate="{ scale: 1, opacity: 1 }" :exit="{ scale: 0, opacity: 0 }"
        :transition="transition" style="display:flex"
      >
        <Check :size="12" :stroke-width="3" />
      </motion.span>
    </AnimatePresence>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { motion, AnimatePresence } from 'motion-v'
import { Check } from 'lucide-vue-next'

// `color` lets a matrix cell render in a specific role's hue (e.g. amber for
// Dealer, teal for Manager, sky blue for Pilot) instead of one flat brand
// color everywhere — pass a CSS color/var, e.g. "var(--role-dealer)".
const props = defineProps({ modelValue: Boolean, disabled: Boolean, color: String, colorSoft: String })
const emit = defineEmits(['update:modelValue', 'change'])
const colorStyle = computed(() => {
  const s = {}
  if (props.color) s['--mcheck-color'] = props.color
  if (props.colorSoft) s['--mcheck-color-soft'] = props.colorSoft
  return s
})

const reduced = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false
const transition = reduced ? { duration: 0 } : { type: 'spring', stiffness: 600, damping: 26 }

function toggle() {
  if (props.disabled) return
  const next = !props.modelValue
  emit('update:modelValue', next)
  emit('change', next)
}
</script>
