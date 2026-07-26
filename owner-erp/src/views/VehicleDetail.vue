<template>
  <div class="topbar">
    <h1><router-link to="/fleet" class="muted">Fleet</router-link> / {{ v?.registration_number || '…' }}</h1>
    <span class="badge" :class="v?.status">{{ v?.status }}</span>
  </div>

  <div class="grid-2">
    <div>
      <p class="section-title">Route history ({{ track.length }} points)</p>
      <FleetMap :markers="markers" :track="trackLatLng" />
    </div>

    <div>
      <p class="section-title">Live telemetry</p>
      <div class="card" style="padding:14px 16px">
        <div class="kvs" v-if="latest">
          <div><span class="muted">Speed</span><b>{{ fmt(latest.speed_kmph) }} km/h</b></div>
          <div><span class="muted">Fuel</span><b>{{ fmt(latest.total_litres) }} L</b></div>
          <div><span class="muted">Lock</span><b>{{ latest.lock_active ? '🔒 locked' : '🔓 open' }}</b></div>
          <div><span class="muted">GPS fix</span><b>{{ latest.has_gps_fix ? `yes (${latest.satellites} sats)` : 'no' }}</b></div>
          <div><span class="muted">GSM</span><b>{{ latest.gsm_signal ?? '—' }}</b></div>
          <div><span class="muted">Recording</span><b>{{ latest.recording ? 'yes' : 'no' }}</b></div>
          <div><span class="muted">Updated</span><b>{{ ago(latest.received_at) }}</b></div>
        </div>
        <p v-else class="muted">No telemetry yet.</p>
      </div>

      <div class="card" style="padding:14px 16px;margin-top:14px" v-if="v?.device">
        <p class="section-title">Send command</p>
        <div class="row">
          <button @click="cmd('open')" :disabled="sending">Open lock</button>
          <button @click="cmd('testing')" :disabled="sending">Testing</button>
          <span class="muted">{{ cmdMsg }}</span>
        </div>
      </div>

      <p class="section-title" style="margin-top:18px">Recent trips</p>
      <div class="card" style="padding:6px 0">
        <table>
          <thead><tr><th>Started</th><th>Dist</th><th>Max</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="t in trips" :key="t.id">
              <td>{{ new Date(t.started_at).toLocaleString() }}</td>
              <td>{{ fmt(t.distance_km) }} km</td>
              <td>{{ fmt(t.max_speed_kmph, 0) }}</td>
              <td><span class="badge" :class="t.status==='active'?'active':'offline'">{{ t.status }}</span></td>
            </tr>
            <tr v-if="!trips.length"><td colspan="4" class="muted" style="padding:14px">No trips.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { getVehicle, getVehicleTrack, getVehicleTrips, sendCommand } from '../api'
import { fmt, ago } from '../util'
import FleetMap from '../components/FleetMap.vue'

const props = defineProps({ id: [String, Number] })
const v = ref(null)
const track = ref([])
const trips = ref([])
const sending = ref(false)
const cmdMsg = ref('')
let timer

const latest = computed(() => v.value?.latest)
const trackLatLng = computed(() => track.value.map((p) => [p.latitude, p.longitude]))
const markers = computed(() =>
  latest.value?.has_gps_fix
    ? [{ id: v.value.id, lat: latest.value.latitude, lng: latest.value.longitude, label: v.value.registration_number, status: v.value.status }]
    : [])

async function load() {
  v.value = await getVehicle(props.id)
  ;[track.value, trips.value] = await Promise.all([
    getVehicleTrack(props.id, 1000), getVehicleTrips(props.id),
  ])
}
async function cmd(payload) {
  if (!v.value?.device) return
  sending.value = true; cmdMsg.value = ''
  try { await sendCommand(v.value.device.id, payload); cmdMsg.value = `Queued "${payload}"` }
  catch { cmdMsg.value = 'Failed' }
  finally { sending.value = false }
}

onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.kvs { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 18px; }
.kvs div { display: flex; flex-direction: column; }
.kvs b { font-size: 16px; margin-top: 2px; }
</style>
