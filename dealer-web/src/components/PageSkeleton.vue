<template>
  <div class="page-skel" aria-hidden="true">
    <div class="skel" style="height:26px;width:260px;max-width:60%;margin:0 0 10px"></div>
    <div class="skel" style="height:14px;width:420px;max-width:80%;margin:0 0 24px"></div>
    <div class="kpis">
      <div class="skel sk-chip" v-for="n in 4" :key="n"></div>
    </div>
    <div class="skel sk-hero"></div>
    <div class="skel sk-row" v-for="n in 4" :key="'r'+n"></div>
  </div>
</template>

<script setup>
// Shown only while a lazy route chunk is still downloading (App.vue); views
// own their own skeletons for their data fetches.
</script>
