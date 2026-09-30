<template>
  <div class="empty">
    <span class="empty-icon" aria-hidden="true"><component :is="icon || Inbox" :size="20" /></span>
    <h3>{{ title }}</h3>
    <p v-if="text">{{ text }}</p>
    <slot />
  </div>
</template>

<script setup>
import { Inbox } from 'lucide-vue-next'
defineProps({ title: String, text: String, icon: [Object, Function] })
</script>
