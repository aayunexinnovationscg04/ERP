<template>
  <div class="topbar">
    <h1><router-link to="/fleet" class="muted">Fleet</router-link> / {{ v?.registration_number || '…' }}</h1>
    <span class="badge" :class="v?.status">{{ v?.status }}</span>
  </div>

  <div v-if="loading" class="grid-2">
    <div>
      <p class="section-title">Route history</p>
      <div class="skel sk-map"></div>
    </div>
    <div>
      <p class="section-title">Live telemetry</p>
      <div class="card" style="padding:16px">
        <div class="skel skel-line lg"></div>
        <div class="skel skel-line md"></div>
        <div class="skel skel-line lg"></div>
        <div class="skel skel-line sm"></div>
        <div class="skel skel-line md"></div>
      </div>
    </div>
  </div>

  <div v-else class="grid-2">
    <div>
      <p class="section-title">Route history ({{ track.length }} points)</p>
      <FleetMap :markers="markers" :track="trackLatLng" />
    </div>

    <div>
      <p class="section-title">Live telemetry</p>
      <div class="card" style="padding:14px 16px">
        <div class="kvs" v-if="latest">
          <div><span class="muted">Speed</span><b class="ico"><Gauge :size="15" /> {{ fmt(latest.speed_kmph) }} km/h</b></div>
          <div><span class="muted">Fuel</span><b class="ico"><Droplet :size="15" /> {{ fmt(latest.total_litres) }} L</b></div>
          <div><span class="muted">Lock</span><b class="ico"><component :is="latest.lock_active ? Lock : LockOpen" :size="15" /> {{ latest.lock_active ? 'locked' : 'open' }}</b></div>
          <div><span class="muted">GPS fix</span><b>{{ latest.has_gps_fix ? `yes (${latest.satellites} sats)` : 'no' }}</b></div>
          <div><span class="muted">GSM</span><b>{{ latest.gsm_signal ?? '—' }}</b></div>
          <div><span class="muted">Recording</span><b>{{ latest.recording ? 'yes' : 'no' }}</b></div>
          <div><span class="muted">Updated</span><b>{{ ago(latest.received_at) }}</b></div>
        </div>
        <p v-else class="muted">No telemetry yet.</p>
      </div>

      <div class="card" style="padding:14px 16px;margin-top:14px" v-if="spark">
        <p class="section-title" style="margin-top:0">Speed trend</p>
        <svg class="spark" :viewBox="`0 0 ${spark.W} ${spark.H}`" preserveAspectRatio="none"
             role="img" :aria-label="`Speed trend over recent telemetry — current ${fmt(curSpeed, 0)} km/h, max ${fmt(maxSpeed, 0)} km/h`">
          <line :x1="0" :y1="spark.base" :x2="spark.W" :y2="spark.base"
                stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
          <polyline :points="spark.area" fill="var(--brand)" fill-opacity="0.10" stroke="none" />
          <polyline :points="spark.line" fill="none" stroke="var(--brand)" stroke-width="1.5"
                    stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
        </svg>
        <div class="row" style="justify-content:space-between;margin-top:6px">
          <span class="muted" style="font-size:12px">Current <b style="color:var(--text)">{{ fmt(curSpeed, 0) }}</b> km/h</span>
          <span class="muted" style="font-size:12px">Max <b style="color:var(--text)">{{ fmt(maxSpeed, 0) }}</b> km/h</span>
        </div>
      </div>

      <div class="card" style="padding:14px 16px;margin-top:14px" v-if="v?.device && canWrite">
        <p class="section-title">Send command</p>
        <div class="row">
          <button class="ico" @click="cmd('open')" :disabled="sending"><LockOpen :size="16" /> Open lock</button>
          <button class="ico" @click="cmd('testing')" :disabled="sending"><Send :size="16" /> Testing</button>
          <span class="muted">{{ cmdMsg }}</span>
        </div>
      </div>
      <p v-else-if="v?.device && !canWrite" class="viewonly" style="margin-top:14px">
        <Lock :size="14" /> View-only — ask an admin to enable editing.
      </p>

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
import { Gauge, Droplet, Lock, LockOpen, Send } from 'lucide-vue-next'
import { getVehicle, getVehicleTrack, getVehicleTrips, sendCommand } from '../api'
import { auth } from '../auth'
import { fmt, ago } from '../util'
import { toast } from '../toast'
import FleetMap from '../components/FleetMap.vue'

const canWrite = computed(() => auth.user?.may_write !== false)

const props = defineProps({ id: [String, Number] })
const v = ref(null)
const track = ref([])
const trips = ref([])
const loading = ref(true)
const sending = ref(false)
const cmdMsg = ref('')
let timer

const latest = computed(() => v.value?.latest)
const trackLatLng = computed(() => track.value.map((p) => [p.latitude, p.longitude]))
const markers = computed(() =>
  latest.value?.has_gps_fix
    ? [{ id: v.value.id, lat: latest.value.latitude, lng: latest.value.longitude, label: v.value.registration_number, status: v.value.status, speed: fmt(latest.value.speed_kmph, 0) }]
    : [])

// --- speed sparkline from recent telemetry ---
const speeds = computed(() =>
  track.value.map((p) => Number(p.speed_kmph)).filter((n) => Number.isFinite(n)))
const maxSpeed = computed(() => (speeds.value.length ? Math.max(...speeds.value) : 0))
const curSpeed = computed(() => latest.value?.speed_kmph ?? speeds.value[speeds.value.length - 1])
const spark = computed(() => {
  const s = speeds.value
  if (s.length < 2) return null
  const W = 300, H = 80, pad = 6
  const base = H - pad
  const max = Math.max(...s, 1)
  const n = s.length
  const px = (i) => pad + (i / (n - 1)) * (W - pad * 2)
  const py = (val) => base - (val / max) * (H - pad * 2)
  const line = s.map((val, i) => `${px(i).toFixed(1)},${py(val).toFixed(1)}`).join(' ')
  const area = `${pad},${base} ${line} ${(W - pad).toFixed(1)},${base}`
  return { W, H, base, line, area }
})

async function load() {
  try {
    v.value = await getVehicle(props.id)
    ;[track.value, trips.value] = await Promise.all([
      getVehicleTrack(props.id, 1000), getVehicleTrips(props.id),
    ])
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
async function cmd(payload) {
  if (!v.value?.device) return
  sending.value = true; cmdMsg.value = ''
  try { await sendCommand(v.value.device.id, payload); cmdMsg.value = `Queued "${payload}"`; toast.success('Command queued') }
  catch { cmdMsg.value = 'Failed'; toast.error('Could not send command') }
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
