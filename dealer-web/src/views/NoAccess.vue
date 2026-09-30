<template>
  <div class="card">
    <EmptyState :icon="ShieldOff" title="No sections enabled for your account"
                text="Ask your administrator for access." />
  </div>
</template>

<script setup>
import { ShieldOff } from 'lucide-vue-next'
import EmptyState from '../components/EmptyState.vue'
</script>
