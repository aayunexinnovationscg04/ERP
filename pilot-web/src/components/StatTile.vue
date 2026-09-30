<template>
  <component :is="to ? 'router-link' : 'div'" :to="to" class="stat" :class="'tone-' + tone">
    <span v-if="icon" class="stat-icon"><component :is="icon" :size="16" /></span>
    <span class="stat-label">{{ label }}</span>
    <span class="stat-value" :title="String(value) + (unit ? ' ' + unit : '')">{{ value }}<small v-if="unit">{{ unit }}</small></span>
  </component>
</template>

<script setup>
// One cell of the slim stats bar (`.kpis`): icon + label + value, no caption.
// `sub` is still accepted (ignored) so older call sites keep working.
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: '—' },
  unit: { type: String, default: '' },
  sub: { type: String, default: '' },
  icon: { type: [Object, Function], default: null },
  tone: { type: String, default: 'gray' }, // brand|blue|green|amber|crit|red|teal|navy|gray
  to: { type: [String, Object], default: null },
})
</script>
