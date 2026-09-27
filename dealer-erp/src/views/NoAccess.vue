<template>
  <PageHeader title="No access" description="Your account is signed in but has no sections enabled." />
  <div class="card">
    <EmptyState :icon="ShieldOff" title="No sections enabled for your account"
                text="Ask your Aayunex administrator to turn on the sections you need, then sign in again." />
  </div>
</template>

<script setup>
import { ShieldOff } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'
</script>
