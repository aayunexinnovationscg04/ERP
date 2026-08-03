<template>
  <button
    type="button" class="toggle" :class="{ on: modelValue }" :disabled="disabled"
    role="switch" :aria-checked="modelValue" @click="toggle"
  >
    <motion.span class="thumb" :animate="{ x: modelValue ? 18 : 0 }" :transition="transition" />
  </button>
</template>

<script setup>
import { motion } from 'motion-v'

const props = defineProps({ modelValue: Boolean, disabled: Boolean })
const emit = defineEmits(['update:modelValue', 'change'])

const reduced = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false
const transition = reduced ? { duration: 0 } : { type: 'spring', stiffness: 520, damping: 32 }

function toggle() {
  if (props.disabled) return
  const next = !props.modelValue
  emit('update:modelValue', next)
  emit('change', next)
}
</script>
