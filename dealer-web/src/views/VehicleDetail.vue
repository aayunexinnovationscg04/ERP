<template>
  <PageHeader :title="v ? v.local_name : 'Vehicle'" :back="{ to: '/vehicles', label: 'Vehicles' }">
    <template #badge>
      <span v-if="v" class="badge" :class="v.status">{{ v.status }}</span>
    </template>
    <template #description>
      <span v-if="v">{{ v.registration_number }}<template v-if="v.make || v.model"> · {{ [v.make, v.model].filter(Boolean).join(' ') }}</template>
        · updated {{ ago(latest?.received_at) }}</span>
    </template>
    <button v-if="v && canWrite" type="button" @click="renaming = true"><Pencil :size="15" /> Rename</button>
    <router-link v-if="v && canOpen('/fuel')" :to="`/fuel/${v.id}`" class="btn"><Fuel :size="16" /> Fuel details</router-link>
  </PageHeader>

  <div v-if="loading" class="grid-2">
    <div class="skel sk-map"></div>
    <div class="card card-body">
      <div class="skel skel-line lg" v-for="n in 6" :key="n"></div>
    </div>
  </div>

  <EmptyState v-else-if="!v" class="card" :icon="TruckIcon" title="Vehicle not found"
    text="">
    <router-link to="/vehicles" class="btn">Back to vehicles</router-link>
  </EmptyState>

  <template v-else>
    <!-- live metric strip -->
    <div class="kpis">
      <StatTile label="Speed" :value="latest ? fmt(latest.speed_kmph, 0) : '—'" :unit="latest ? 'km/h' : ''" :icon="Gauge" tone="blue" />
      <StatTile label="Fuel" :value="latest?.total_litres != null ? fmt(latest.total_litres) : '—'" :unit="latest?.total_litres != null ? 'L' : ''"
        :icon="Droplet" tone="brand" />
      <StatTile label="Fuel lock" :value="latest ? (latest.lock_active ? 'Locked' : 'Open') : '—'" :icon="latest?.lock_active ? Lock : LockOpen"
        :tone="latest?.lock_active ? 'green' : 'amber'" />
      <StatTile label="GPS" :value="latest ? (latest.has_gps_fix ? `Fixed · ${latest.satellites ?? 0} sats` : 'No fix') : '—'" :icon="Satellite" :tone="latest?.has_gps_fix ? 'green' : 'gray'" />
    </div>

    <div class="grid-2">
      <div class="stack">
        <div class="card flush">
          <div class="card-head">
            <div class="card-head-title"><RouteIcon :size="17" /><h2>Route history</h2></div>
          </div>
          <FleetMap :markers="markers" :track="trackLatLng" height="420px" />
        </div>

        <div class="card" v-if="spark">
          <div class="card-head"><div class="card-head-title"><Activity :size="17" /><h2>Speed trend</h2></div></div>
          <div class="card-body">
            <svg class="spark" :viewBox="`0 0 ${spark.W} ${spark.H}`" preserveAspectRatio="none"
                 role="img" :aria-label="`Speed trend — current ${fmt(curSpeed, 0)} km/h, max ${fmt(maxSpeed, 0)} km/h`">
              <line :x1="0" :y1="spark.base" :x2="spark.W" :y2="spark.base" stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
              <polyline :points="spark.area" fill="var(--info)" fill-opacity="0.12" stroke="none" />
              <polyline :points="spark.line" fill="none" stroke="var(--info)" stroke-width="2"
                        stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
            </svg>
            <div class="legend-row">
              <span>Current <b>{{ fmt(curSpeed, 0) }}</b> km/h</span>
              <span>Max <b>{{ fmt(maxSpeed, 0) }}</b> km/h</span>
            </div>
          </div>
        </div>
      </div>

      <div class="stack">
        <div class="card">
          <div class="card-head"><div class="card-head-title"><Radio :size="17" /><h2>Live telemetry</h2></div>
            <span class="muted" style="font-size:12.5px">{{ ago(latest?.received_at) }}</span></div>
          <div class="card-body">
            <div class="kvs" v-if="latest">
              <div><span class="k">GSM signal</span><span class="v">{{ latest.gsm_signal != null ? latest.gsm_signal + ' dBm' : '—' }}</span></div>
              <div><span class="k">Recording</span><span class="v">{{ latest.recording ? 'Yes' : 'No' }}</span></div>
              <div><span class="k">Altitude</span><span class="v">{{ latest.altitude_m != null ? fmt(latest.altitude_m, 0) + ' m' : '—' }}</span></div>
              <div><span class="k">Flow rate</span><span class="v">{{ latest.flow_rate_lpm != null ? fmt(latest.flow_rate_lpm) + ' L/min' : '—' }}</span></div>
              <div v-if="latest.has_gps_fix" style="grid-column:1/-1"><span class="k">Position</span>
                <span class="v num">{{ Number(latest.latitude).toFixed(5) }}, {{ Number(latest.longitude).toFixed(5) }}</span></div>
            </div>
            <p v-else class="muted">No telemetry received yet.</p>
          </div>
        </div>

        <div class="card">
          <div class="card-head"><div class="card-head-title"><IdCard :size="17" /><h2>Vehicle &amp; pilot</h2></div></div>
          <div class="card-body">
            <div class="kvs">
              <div><span class="k">Make / model</span><span class="v">{{ v.make || v.model ? [v.make, v.model].filter(Boolean).join(' ') : '—' }}</span></div>
              <div><span class="k">Tank capacity</span><span class="v">{{ v.tank_capacity_litres ? v.tank_capacity_litres + ' L' : '—' }}</span></div>
              <div><span class="k">Device</span><span class="v">{{ v.device?.device_id || 'Not linked' }}</span></div>
              <div><span class="k">SIM</span><span class="v">{{ v.device?.sim_number || '—' }}</span></div>
            </div>
            <div class="pilot-row">
              <span class="avatar-sm"><UserRound :size="16" /></span>
              <div v-if="v.active_pilot" style="min-width:0">
                <div class="cell-main">{{ v.active_pilot.name }}</div>
                <div class="cell-sub">{{ v.active_pilot.phone || '—' }} · Licence {{ v.active_pilot.license_no || '—' }}</div>
              </div>
              <div v-else class="muted">No pilot assigned</div>
              <router-link v-if="v.active_pilot" :to="`/pilots/${v.active_pilot.id}`" class="row-link" style="margin-left:auto" title="Open pilot"><ChevronRight :size="17" /></router-link>
            </div>
          </div>
        </div>

        <div class="card flush">
          <div class="card-head"><div class="card-head-title"><FileText :size="17" /><h2>Documents</h2></div></div>
          <div v-if="v.documents?.length" class="list">
            <div class="list-row" v-for="d in v.documents" :key="d.id">
              <span class="grow">
                <div class="title">{{ d.doc_type_label }}</div>
                <div class="sub">{{ d.number || '—' }}<template v-if="d.expiry_date"> · expires {{ d.expiry_date }}</template></div>
              </span>
              <span class="badge" :class="expiryBadge[d.expiry_status]">{{ expiryLabel[d.expiry_status] }}</span>
            </div>
          </div>
          <EmptyState v-else compact :icon="FileText" title="No documents on file" />
        </div>

        <div class="card" v-if="v.device && canWrite">
          <div class="card-head"><div class="card-head-title"><Send :size="17" /><h2>Device commands</h2></div></div>
          <div class="card-body">
            <div class="row wrap">
              <button @click="cmd('open')" :disabled="sending"><LockOpen :size="16" /> Open lock</button>
              <button @click="cmd('testing')" :disabled="sending"><Send :size="16" /> Send test</button>
              <span class="muted" style="font-size:12.5px">{{ cmdMsg }}</span>
            </div>
          </div>
        </div>

        <div class="card" v-if="v.latest_raw">
          <div class="card-head">
            <div class="card-head-title"><FileCode :size="17" /><h2>Last raw payload</h2></div>
            <button type="button" class="sm" @click="showRaw = !showRaw">
              <component :is="showRaw ? EyeOff : Eye" :size="15" /> {{ showRaw ? 'Hide' : 'Show' }}
            </button>
          </div>
          <div v-if="showRaw" class="card-body"><pre class="raw-json">{{ prettyRaw }}</pre></div>
        </div>
      </div>
    </div>

    <div class="card flush section">
      <div class="card-head"><div class="card-head-title"><RouteIcon :size="17" /><h2>Recent trips</h2></div></div>
      <div class="table-wrap" v-if="trips.length">
        <table class="mstack">
          <thead><tr><th>Started</th><th>Ended</th><th class="num">Distance</th><th class="num">Avg / max speed</th><th class="num">Fuel used</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="t in pager.rows.value" :key="t.id">
              <td class="nowrap cell-head"><span class="cell-main">{{ dt(t.started_at) }}</span><span class="badge show-sm" :class="t.status === 'active' ? 'active' : 'offline'">{{ t.status }}</span></td>
              <td class="nowrap muted" data-label="Ended">{{ t.ended_at ? dt(t.ended_at) : 'In progress' }}</td>
              <td class="num" data-label="Distance">{{ fmt(t.distance_km) }} km</td>
              <td class="num" data-label="Avg / max">{{ fmt(t.avg_speed_kmph, 0) }} / {{ fmt(t.max_speed_kmph, 0) }} km/h</td>
              <td class="num" data-label="Fuel used">{{ t.fuel_consumed_litres != null ? fmt(t.fuel_consumed_litres) + ' L' : '—' }}</td>
              <td class="hide-sm"><span class="badge" :class="t.status === 'active' ? 'active' : 'offline'">{{ t.status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-else compact :icon="RouteIcon" title="No trips recorded yet" />
      <Pager v-if="trips.length" :pager="pager" />
    </div>
  </template>

  <RenameVehicleModal v-if="renaming && v" :vehicle="v" @close="renaming = false" @saved="(n) => { v.local_name = n }" />
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import {
  Gauge, Droplet, Lock, LockOpen, Send, FileCode, Eye, EyeOff, Fuel, Pencil, Satellite, Activity, Radio,
  IdCard, UserRound, ChevronRight, FileText, Route as RouteIcon, Truck as TruckIcon,
} from 'lucide-vue-next'
import { getVehicle, getVehicleTrack, getVehicleTrips, sendCommand } from '../api'
import { auth } from '../auth'
import { fmt, ago } from '../util'
import { toast } from '../toast'
import FleetMap from '../components/FleetMap.vue'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import RenameVehicleModal from '../components/RenameVehicleModal.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { canOpen } from '../access'

const canWrite = computed(() => auth.user?.may_write !== false)
const expiryLabel = { valid: 'Valid', expiring_soon: 'Expiring soon', expired: 'Expired', unknown: 'No expiry set' }
const expiryBadge = { valid: 'active', expiring_soon: 'idle', expired: 'critical', unknown: 'offline' }

const props = defineProps({ id: [String, Number] })
const v = ref(null)
const track = ref([])
const trips = ref([])
const loading = ref(true)
const sending = ref(false)
const cmdMsg = ref('')
const renaming = ref(false)
let timer
const pager = usePaging(trips, 10)

const dt = (iso) => new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
const latest = computed(() => v.value?.latest)
const prettyRaw = computed(() => JSON.stringify(v.value?.latest_raw ?? {}, null, 2))
const showRaw = ref(false)
const trackLatLng = computed(() => track.value.map((p) => [p.latitude, p.longitude]))
const markers = computed(() =>
  latest.value?.has_gps_fix
    ? [{ id: v.value.id, lat: latest.value.latitude, lng: latest.value.longitude, label: v.value.registration_number, status: v.value.status, speed: fmt(latest.value.speed_kmph, 0) }]
    : [])

const speeds = computed(() => track.value.map((p) => Number(p.speed_kmph)).filter((n) => Number.isFinite(n)))
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
    ;[track.value, trips.value] = await Promise.all([getVehicleTrack(props.id, 1000), getVehicleTrips(props.id)])
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
async function cmd(payload) {
  if (!v.value?.device) return
  sending.value = true; cmdMsg.value = ''
  try { await sendCommand(v.value.device.id, payload); cmdMsg.value = `Queued “${payload}”`; toast.success('Command queued') }
  catch { cmdMsg.value = 'Failed'; toast.error('Could not send command') }
  finally { sending.value = false }
}

onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.pilot-row {
  display: flex; align-items: center; gap: 12px;
  margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--border);
}
.avatar-sm { width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center; flex: none; background: var(--info-soft); color: var(--info); }
.raw-json {
  margin: 0; max-height: 320px; overflow: auto; font-size: 12px; line-height: 1.55; font-family: var(--font-mono);
  background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius-sm);
  padding: 12px 14px; white-space: pre-wrap; word-break: break-all;
}
</style>
