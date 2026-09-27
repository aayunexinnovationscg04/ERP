<template>
  <header class="page-head">
    <div class="ph-main">
      <span v-if="icon" class="ph-icon" aria-hidden="true"><component :is="icon" :size="20" /></span>
      <div class="ph-text">
        <h1>{{ title }}</h1>
        <p v-if="description || $slots.description"><slot name="description">{{ description }}</slot></p>
      </div>
    </div>
    <div v-if="$slots.default" class="ph-actions"><slot /></div>
  </header>
</template>

<script setup>
// Consistent page header: icon + title + one-line description on the left,
// page-level actions (primary action last) on the right.
defineProps({ title: String, description: String, icon: [Object, Function] })
</script>
