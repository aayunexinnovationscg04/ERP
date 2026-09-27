<template>
  <div class="page-skel" aria-hidden="true">
    <div class="skel sk-title"></div>
    <div class="stat-grid">
      <div class="skel sk-chip" v-for="n in 2" :key="n"></div>
    </div>
    <div class="skel sk-item" v-for="n in 4" :key="'r'+n" style="margin-top:12px"></div>
  </div>
</template>

<script setup>
// Generic fallback shown only while a lazy route chunk is still downloading
// (App.vue brackets it with router.beforeEach/afterEach and a 150ms delay).
// Individual views own their own skeleton for their data fetch.
</script>
