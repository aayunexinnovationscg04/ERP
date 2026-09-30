<template>
  <!-- Shared loading / empty states for trip-only pages. Renders the default
       slot only when a truck is assigned AND it is on an active trip. -->
  <div v-if="state.loading.value">
    <div class="kpis"><div class="skel sk-chip" v-for="n in 3" :key="n"></div></div>
    <div class="skel sk-box" style="margin-bottom:12px"></div>
    <div class="skel sk-row" v-for="n in 3" :key="'r'+n"></div>
  </div>

  <div v-else-if="state.failed.value" class="card">
    <EmptyState :icon="WifiOff" title="Couldn't load your trip">
      <button type="button" class="primary" @click="state.reload()"><RefreshCw :size="16" /> Try again</button>
    </EmptyState>
  </div>

  <div v-else-if="!state.assigned.value" class="card">
    <EmptyState :icon="Truck" title="No truck assigned yet" :text="noTruckText">
      <router-link to="/" class="btn"><Truck :size="16" /> My truck</router-link>
    </EmptyState>
  </div>

  <div v-else-if="!state.onTrip.value" class="card">
    <EmptyState :icon="CirclePause" title="No active trip" :text="noTripText">
      <div class="row wrap" style="justify-content:center">
        <router-link to="/trips" class="btn"><Route :size="16" /> View trips</router-link>
        <button type="button" class="ghost" @click="state.reload()"><RefreshCw :size="16" /> Refresh</button>
      </div>
    </EmptyState>
  </div>

  <slot v-else />
</template>

<script setup>
import { Truck, Route, RefreshCw, CirclePause, WifiOff } from 'lucide-vue-next'
import EmptyState from './EmptyState.vue'

defineProps({
  state: { type: Object, required: true },
  noTruckText: { type: String, default: 'Ask your fleet manager to link one.' },
  noTripText: { type: String, default: 'Shown while your truck is on a trip.' },
})
</script>
