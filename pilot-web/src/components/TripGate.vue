<template>
  <!-- Shared loading / empty states for trip-only pages. Renders the default
       slot only when a truck is assigned AND it is on an active trip. -->
  <div v-if="state.loading.value">
    <div class="skel" style="height:150px; margin-bottom:14px"></div>
    <div class="skel sk-item" v-for="n in 3" :key="n"></div>
  </div>

  <div v-else-if="state.failed.value" class="card empty-state">
    <span class="empty-ic"><WifiOff :size="34" :stroke-width="1.75" /></span>
    <h2>Couldn't load your trip</h2>
    <div class="empty-actions">
      <button type="button" class="btn btn-primary" @click="state.reload()"><RefreshCw :size="18" :stroke-width="2.25" /> Try again</button>
    </div>
  </div>

  <div v-else-if="!state.assigned.value" class="card empty-state">
    <span class="empty-ic"><Truck :size="34" :stroke-width="1.75" /></span>
    <h2>No truck assigned yet</h2>
    <p>{{ noTruckText }}</p>
    <div class="empty-actions">
      <router-link to="/" class="btn"><Truck :size="18" :stroke-width="2.25" /> My truck</router-link>
    </div>
  </div>

  <div v-else-if="!state.onTrip.value" class="card empty-state">
    <span class="empty-ic"><CirclePause :size="34" :stroke-width="1.75" /></span>
    <h2>No active trip</h2>
    <p>{{ noTripText }}</p>
    <div class="empty-actions">
      <router-link to="/trips" class="btn"><Route :size="18" :stroke-width="2.25" /> View trips</router-link>
      <button type="button" class="btn btn-ghost" @click="state.reload()"><RefreshCw :size="18" :stroke-width="2.25" /> Refresh</button>
    </div>
  </div>

  <slot v-else />
</template>

<script setup>
import { Truck, Route, RefreshCw, CirclePause, WifiOff } from 'lucide-vue-next'

defineProps({
  state: { type: Object, required: true },
  noTruckText: { type: String, default: 'Ask your fleet manager to link one.' },
  noTripText: { type: String, default: 'Shown while your truck is on a trip.' },
})
</script>
