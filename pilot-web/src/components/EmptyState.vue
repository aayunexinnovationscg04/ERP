<template>
  <div class="empty-state" :class="{ compact }">
    <span class="es-icon"><component :is="icon" :size="22" /></span>
    <h3>{{ title }}</h3>
    <p v-if="text">{{ text }}</p>
    <div v-if="$slots.default" class="es-action"><slot /></div>
  </div>
</template>

<script setup>
import { Inbox } from 'lucide-vue-next'
defineProps({
  icon: { type: [Object, Function], default: Inbox },
  title: { type: String, required: true },
  text: { type: String, default: '' },
  compact: { type: Boolean, default: false },
})
</script>
