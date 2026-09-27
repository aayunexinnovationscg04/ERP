<template>
  <component :is="to ? 'router-link' : 'div'" :to="to" class="card kpi">
    <div class="kpi-top">
      <span class="kpi-label">{{ label }}</span>
      <span v-if="icon" class="icon-chip" :class="tone"><component :is="icon" :size="17" /></span>
    </div>
    <div class="kpi-value" :title="String(value)">{{ value }}<small v-if="unit">{{ unit }}</small></div>
    <div v-if="sub || $slots.default" class="kpi-sub"><slot>{{ sub }}</slot></div>
  </component>
</template>

<script setup>
// KPI tile: label + tinted icon on top, big tabular number, optional caption.
// Pass `to` to make the whole tile a link into the relevant page.
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: '—' },
  unit: { type: String, default: '' },
  sub: { type: String, default: '' },
  icon: { type: [Object, Function], default: null },
  tone: { type: String, default: 'gray' }, // icon-chip color: brand|blue|green|amber|crit|teal|navy|gray
  to: { type: [String, Object], default: null },
})
</script>
