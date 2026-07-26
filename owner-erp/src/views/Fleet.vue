<template>
  <div class="topbar">
    <h1>Fleet</h1>
    <span class="muted">{{ vehicles.length }} vehicle(s)</span>
  </div>

  <div v-if="loading" style="padding:2px 0">
    <div class="skel sk-row" v-for="n in 6" :key="n"></div>
  </div>

  <div v-else class="card" style="padding:6px 0">
    <table>
      <thead>
        <tr><th></th><th>Vehicle</th><th>Status</th><th>Speed</th><th>Fuel (L)</th><th>Device</th><th>Last seen</th></tr>
      </thead>
      <tbody>
        <tr v-for="v in vehicles" :key="v.id" class="clickable" @click="$router.push(`/vehicles/${v.id}`)">
          <td><span class="dot" :class="freshness(v)"></span></td>
          <td>{{ v.registration_number }}<div class="muted" style="font-size:12px">{{ v.make }} {{ v.model }}</div></td>
          <td><span class="badge" :class="v.status">{{ v.status }}</span></td>
          <td>{{ fmt(v.latest?.speed_kmph) }} km/h</td>
          <td>{{ fmt(v.latest?.total_litres) }}</td>
          <td class="muted">{{ v.device_id || '—' }}</td>
          <td class="muted">{{ ago(v.latest?.received_at) }}</td>
        </tr>
        <tr v-if="!vehicles.length"><td colspan="7" class="muted" style="padding:16px">No vehicles yet.</td></tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { getVehicles } from '../api'
import { freshness, ago, fmt } from '../util'

const vehicles = ref([])
const loading = ref(true)
let timer
async function load() {
  try { vehicles.value = await getVehicles() }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>
