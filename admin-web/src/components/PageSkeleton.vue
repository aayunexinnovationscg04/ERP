<template>
  <div aria-hidden="true">
    <div class="skel" style="height:26px;width:260px;max-width:70%;margin:4px 0 8px"></div>
    <div class="skel" style="height:14px;width:420px;max-width:90%;margin-bottom:24px"></div>
    <div class="stats">
      <div class="stat" v-for="n in 4" :key="n"><div class="skel skel-line sm"></div><div class="skel skel-line md" style="height:24px"></div></div>
    </div>
    <div class="card card-body"><div class="skel skel-row" v-for="n in 5" :key="'r'+n" style="margin-bottom:14px"></div></div>
  </div>
</template>

<script setup>
// Shown only while a lazy route chunk is still downloading (see App.vue).
</script>
