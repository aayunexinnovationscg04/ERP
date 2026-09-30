<template>
  <button
    type="button" class="toggle" :class="{ on: modelValue }" :disabled="disabled"
    role="switch" :aria-checked="modelValue" @click="toggle"
  >
    <span class="thumb" />
  </button>
</template>

<script setup>
// The thumb slides with a CSS transform transition (style.css) — no JS
// animation per switch, so long tables of toggles stay cheap to render.
const props = defineProps({ modelValue: Boolean, disabled: Boolean })
const emit = defineEmits(['update:modelValue', 'change'])

function toggle() {
  if (props.disabled) return
  const next = !props.modelValue
  emit('update:modelValue', next)
  emit('change', next)
}
</script>
