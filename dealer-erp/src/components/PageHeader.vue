<template>
  <header class="page-head">
    <div class="page-head-text">
      <router-link v-if="back" :to="back.to" class="back-link">
        <ArrowLeft :size="15" /> {{ back.label }}
      </router-link>
      <div class="page-head-title">
        <h1>{{ title }}</h1>
        <slot name="badge" />
        <span v-if="preview" class="preview-tag" title="This module has no live data source yet — figures shown are sample data.">
          <FlaskConical :size="12" /> Preview · sample data
        </span>
      </div>
      <p v-if="description || $slots.description" class="page-head-desc">
        <slot name="description">{{ description }}</slot>
      </p>
    </div>
    <div v-if="$slots.default" class="page-head-actions"><slot /></div>
  </header>
</template>

<script setup>
import { ArrowLeft, FlaskConical } from 'lucide-vue-next'

// Consistent page header: title + one-line description + primary actions.
// `back` = { to, label } renders a breadcrumb-style back link above the title.
// `preview` marks modules still running on sample data (see src/mock.js).
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
  back: { type: Object, default: null },
  preview: { type: Boolean, default: false },
})
</script>
