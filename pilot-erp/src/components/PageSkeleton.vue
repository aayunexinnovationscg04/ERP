<template>
  <div class="page-skel" aria-hidden="true">
    <div class="skel skel-line md" style="height:20px;width:40%;margin:0 0 18px"></div>
    <div class="chips">
      <div class="skel sk-chip" v-for="n in 2" :key="n"></div>
    </div>
    <div class="skel sk-item" v-for="n in 4" :key="'r'+n" style="margin-top:12px"></div>
  </div>
</template>

<script setup>
// Generic fallback shown only while a lazy route chunk is still downloading
// (App.vue's `navigating`, bracketed by router.beforeEach/afterEach) — most
// navigations resolve well under the show-delay and never see this at all;
// it exists for the occasional slow/first-load chunk fetch so that moment
// reads as "loading" rather than a frozen or blank page. Individual views
// still own their own skeleton for their real data-fetch beyond this.
</script>

<style scoped>
.page-skel { padding: 4px 2px; }
</style>
