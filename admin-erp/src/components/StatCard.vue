<template>
  <div class="stat" :class="tone ? 'tone-' + tone : ''">
    <div class="stat-top">
      <span class="stat-label">{{ label }}</span>
      <span v-if="icon" class="stat-icon" aria-hidden="true"><component :is="icon" :size="16" /></span>
    </div>
    <div v-if="loading" class="skel skel-line md" style="height:26px;margin:4px 0 2px"></div>
    <div v-else class="stat-value"><slot>{{ value }}</slot></div>
    <div v-if="sub || $slots.sub" class="stat-sub"><slot name="sub">{{ sub }}</slot></div>
  </div>
</template>

<script setup>
defineProps({
  label: String,
  value: [String, Number],
  sub: String,
  icon: [Object, Function],
  tone: String, // brand | green | amber | red | crit | info | navy | teal
  loading: Boolean,
})
</script>
