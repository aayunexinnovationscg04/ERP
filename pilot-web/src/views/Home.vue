<template>
  <PageHeader>
    <button v-if="!loading && assigned" type="button" @click="refresh" :disabled="refreshing" aria-label="Refresh now" title="Refresh now">
      <RefreshCw :size="16" :class="{ spin: refreshing }" /> Refresh
    </button>
  </PageHeader>

  <!-- loading -->
  <template v-if="loading">
    <div class="kpis"><div class="skel sk-chip" v-for="n in 5" :key="n"></div></div>
    <div class="grid-2"><div class="skel sk-map"></div><div class="skel sk-box"></div></div>
  </template>

  <!-- no vehicle assigned -->
  <div v-else-if="!assigned" class="card">
    <EmptyState :icon="Truck" title="No truck assigned yet" text="Ask your fleet manager to link one.">
      <button class="primary" type="button" @click="checkAgain" :disabled="refreshing">
        <RefreshCw :size="16" :class="{ spin: refreshing }" /> Check again
      </button>
    </EmptyState>
  </div>

  <template v-else>
    <div class="kpis home-kpis">
      <StatTile label="Speed" :value="fmt(latest?.speed_kmph)" unit="km/h" :icon="Gauge" tone="brand" />
      <StatTile label="Today" :value="summary.distance_today_km ?? 0" unit="km" :icon="Milestone" tone="blue" />
      <StatTile label="Fuel cap" :value="latest ? (latest.lock_active ? 'Locked' : 'Open') : '—'"
        :icon="latest?.lock_active ? Lock : LockOpen" :tone="latest?.lock_active ? 'green' : 'amber'" />
      <StatTile label="GPS" :value="latest?.has_gps_fix ? `${latest?.satellites ?? 0} sats` : 'No fix'"
        :icon="Satellite" :tone="latest?.has_gps_fix ? 'green' : 'amber'" />
      <StatTile label="Tracker" :value="trackerLabel" :icon="RadioTower" :tone="trackerTone" />
    </div>

    <router-link v-if="summary.open_alerts" to="/alerts" class="alert-banner">
      <span class="icon-chip crit"><ShieldAlert :size="18" /></span>
      <strong>{{ summary.open_alerts }} open alert{{ summary.open_alerts > 1 ? 's' : '' }}</strong>
      <span class="ab-go">Review <ChevronRight :size="16" /></span>
    </router-link>

    <div class="grid-2 home-grid">
      <!-- live map -->
      <section class="card flush map-card" aria-label="Live location">
        <div class="card-head">
          <div class="card-head-title"><MapPin :size="18" /><h2>Live location</h2></div>
          <span class="hero-foot">
            <span class="live-dot" :class="{ stale: isStale }" aria-hidden="true"></span>
            Updated {{ latest ? timeAgo(latest.received_at, nowTick) : '—' }}
          </span>
        </div>
        <FleetMap :markers="markers" :track="track" empty-text="Waiting for a GPS fix" />
      </section>

      <div class="stack">
        <!-- vehicle -->
        <section class="card hero" aria-label="Vehicle status">
          <div class="card-head">
            <div class="card-head-title"><Truck :size="18" /><h2>Vehicle</h2></div>
            <span class="badge nt trip-badge" :class="summary.on_trip ? 'active' : 'offline'">{{ summary.on_trip ? 'On trip' : 'Parked' }}</span>
          </div>
          <div class="card-body">
            <span class="plate">{{ v.registration_number }}</span>
            <div class="hero-model">
              <span>{{ modelLine }}</span>
              <span class="badge" :class="v.status">{{ statusLabel(v.status) }}</span>
            </div>
            <div class="kvs" style="margin-top:14px">
              <div><span class="k">Motion</span><span class="v">{{ latest?.speed_kmph == null ? 'No reading' : latest.speed_kmph > 2 ? 'Moving' : 'Stopped' }}</span></div>
              <div><span class="k">Last reading</span><span class="v" :title="latest ? dateTime(latest.received_at) : ''">{{ latest ? timeAgo(latest.received_at, nowTick) : '—' }}</span></div>
            </div>
          </div>
        </section>

        <!-- speed trend -->
        <section v-if="spark" class="card" aria-label="Speed trend">
          <div class="card-head">
            <div class="card-head-title"><Activity :size="18" /><h2>Speed trend</h2></div>
            <span class="peak"><span class="muted">Peak</span> <strong class="num">{{ spark.max }}</strong> <span class="muted">km/h</span></span>
          </div>
          <div class="card-body">
            <svg class="spark" :viewBox="`0 0 ${spark.w} ${spark.h}`" preserveAspectRatio="none" role="img"
              :aria-label="`Speed over the last ${spark.n} readings, currently ${spark.last} km/h, peak ${spark.max} km/h`">
              <line x1="0" :y1="spark.base" :x2="spark.w" :y2="spark.base" stroke="var(--border-strong)" stroke-width="1" vector-effect="non-scaling-stroke" />
              <polyline :points="spark.area" fill="var(--brand)" fill-opacity=".12" stroke="none" />
              <polyline :points="spark.line" fill="none" stroke="var(--brand)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
            </svg>
          </div>
        </section>

        <!-- documents -->
        <section v-if="docs.length" class="card flush docs-card" aria-label="Vehicle documents">
          <div class="card-head">
            <div class="card-head-title"><FileText :size="18" /><h2>Documents</h2></div>
            <span v-if="docIssues" class="badge nt" :class="docsExpired ? 'critical' : 'warning'">{{ docIssues }} to renew</span>
            <span v-else class="badge green">All valid</span>
          </div>
          <div class="list">
            <div v-for="d in docs" :key="d.id" class="list-row">
              <span class="icon-chip" :class="docTone(d.expiry_status)"><component :is="docIcon(d.expiry_status)" :size="16" /></span>
              <div class="grow">
                <div class="title">{{ d.doc_type_label }}</div>
                <div v-if="docSub(d)" class="sub">{{ docSub(d) }}</div>
              </div>
              <span class="badge" :class="docBadge(d.expiry_status)">{{ docStatusLabel(d.expiry_status) }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>

  </template>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import {
  Truck, Gauge, Milestone, Lock, LockOpen, Satellite, ShieldAlert, RefreshCw, MapPin, Activity,
  ChevronRight, RadioTower, FileText, FileCheck, FileClock, FileX,
} from 'lucide-vue-next'
import FleetMap from '../components/FleetMap.vue'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import { getSummary, getMyTrack, getMyVehicle } from '../api'
import { toast } from '../toast'
import { timeAgo, shortDate, dateTime } from '../format'

const loading = ref(true)
const refreshing = ref(false)
const summary = ref({})
const vehicle = ref(null)
const track = ref([])
const speeds = ref([])
const nowTick = ref(Date.now())
let timer = null, tick = null

const assigned = computed(() => summary.value.assigned)
const v = computed(() => summary.value.vehicle || {})
const latest = computed(() => summary.value.latest)
const modelLine = computed(() => {
  const mm = [v.value.make, v.value.model].filter(Boolean).join(' ') || 'Vehicle'
  return vehicle.value?.local_name ? `${mm} · ${vehicle.value.local_name}` : mm
})
const isStale = computed(() => !latest.value || nowTick.value - new Date(latest.value.received_at).getTime() > 10 * 60000)

const device = computed(() => vehicle.value?.device || null)
const trackerLabel = computed(() => {
  if (!vehicle.value) return '—'
  if (!device.value) return 'Not fitted'
  return device.value.online ? 'Online' : 'Offline'
})
const trackerTone = computed(() => (!device.value ? 'gray' : device.value.online ? 'green' : 'red'))

const markers = computed(() => {
  const l = latest.value
  if (!l || !l.has_gps_fix) return []
  return [{ id: v.value.id, lat: l.latitude, lng: l.longitude, label: v.value.registration_number, status: v.value.status }]
})

function fmt(n) { return n == null ? '—' : Math.round(n) }
function statusLabel(s) { const t = s ? s.replace(/_/g, ' ') : 'unknown'; return t.charAt(0).toUpperCase() + t.slice(1) }

// ---- documents (from /pilot/vehicle) ----
const DOC_ORDER = { expired: 0, expiring_soon: 1, valid: 2 }
const docs = computed(() => [...(vehicle.value?.documents || [])]
  .sort((a, b) => (DOC_ORDER[a.expiry_status] ?? 3) - (DOC_ORDER[b.expiry_status] ?? 3)))
const docIssues = computed(() => docs.value.filter((d) => d.expiry_status === 'expired' || d.expiry_status === 'expiring_soon').length)
const docsExpired = computed(() => docs.value.some((d) => d.expiry_status === 'expired'))
function docTone(s) { return s === 'expired' ? 'red' : s === 'expiring_soon' ? 'amber' : 'green' }
function docBadge(s) { return s === 'expired' ? 'critical' : s === 'expiring_soon' ? 'warning' : s === 'valid' ? 'green' : 'gray' }
function docIcon(s) { return s === 'expired' ? FileX : s === 'expiring_soon' ? FileClock : FileCheck }
function docSub(d) {
  const exp = d.expiry_date ? (d.expiry_status === 'expired' ? 'Expired ' : 'Valid till ') + shortDate(d.expiry_date) : ''
  return [d.number, exp].filter(Boolean).join(' · ')
}
function docStatusLabel(s) { return s === 'expired' ? 'Expired' : s === 'expiring_soon' ? 'Expiring' : s === 'valid' ? 'Valid' : '—' }

// ---- speed sparkline (inline SVG from recent telemetry) ----
const spark = computed(() => {
  const arr = speeds.value.slice(-60)
  if (arr.length < 2) return null
  const w = 300, h = 100, pad = 6
  const max = Math.max(...arr)
  const top = max || 1
  const n = arr.length
  const X = (i) => (i / (n - 1)) * w
  const Y = (val) => pad + (1 - val / top) * (h - pad * 2)
  const line = arr.map((val, i) => `${X(i).toFixed(1)},${Y(val).toFixed(1)}`).join(' ')
  const base = (h - pad).toFixed(1)
  const area = `0,${base} ${line} ${w},${base}`
  return { line, area, w, h, base, n, max: Math.round(max), last: Math.round(arr[n - 1]) }
})

async function load() {
  try {
    summary.value = await getSummary()
    if (summary.value.assigned) {
      const [pts, veh] = await Promise.all([getMyTrack(500), getMyVehicle().catch(() => null)])
      // telemetry arrives newest-first; draw the route oldest -> newest
      const ordered = [...pts].sort((a, b) => new Date(a.received_at) - new Date(b.received_at))
      track.value = ordered.filter((p) => p.has_gps_fix).map((p) => [p.latitude, p.longitude])
      speeds.value = ordered.filter((p) => p.speed_kmph != null).map((p) => p.speed_kmph)
      if (veh) vehicle.value = veh
    }
    return true
  } catch (e) { return false /* keep last good data */ }
  finally { loading.value = false; nowTick.value = Date.now() }
}

async function refresh() {
  refreshing.value = true
  const ok = await load()
  refreshing.value = false
  if (!ok) toast.error('Could not refresh. Check your connection.')
}
async function checkAgain() {
  refreshing.value = true
  const ok = await load()
  refreshing.value = false
  if (!ok) toast.error('Could not reach the server. Try again in a moment.')
  else if (!summary.value.assigned) toast.info('Still no truck assigned.')
  else toast.success('Truck assigned.')
}

onMounted(() => {
  load()
  timer = setInterval(load, 20000)
  tick = setInterval(() => { nowTick.value = Date.now() }, 30000)
})
onBeforeUnmount(() => { clearInterval(timer); clearInterval(tick) })
</script>

<style scoped>
.hero-foot { display: inline-flex; align-items: center; gap: 7px; font-size: 12.5px; font-weight: 600; color: var(--muted); white-space: nowrap; }
.live-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); flex: none; }
.live-dot.stale { background: var(--amber); }

/* Indian number-plate styling: white plate, dark border, heavy letters */
.plate {
  display: inline-block; max-width: 100%; padding: 4px 11px; border-radius: var(--radius-xs);
  background: #FFFFFF; color: var(--navy-900); border: 2px solid var(--navy-900);
  font-size: 1.25rem; font-weight: 800; letter-spacing: .06em; line-height: 1.2;
  font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
:root[data-theme="dark"] .plate { border-color: #CBD5E1; }
.hero-model { display: flex; align-items: center; flex-wrap: wrap; gap: 6px 10px; color: var(--muted); font-size: 13.5px; font-weight: 600; margin-top: 10px; }

.alert-banner {
  display: flex; align-items: center; gap: 12px; min-height: 52px; padding: 8px 14px; margin-bottom: 12px;
  border-radius: var(--radius); background: var(--crit-soft); border: 1px solid var(--crit);
  color: var(--text); text-decoration: none;
}
.alert-banner:hover { text-decoration: none; background: var(--red-soft); }
.alert-banner strong { flex: 1; min-width: 0; color: var(--ink-strong); font-size: 14px; }
.ab-go { flex: none; display: inline-flex; align-items: center; gap: 2px; font-weight: 700; font-size: 13px; color: var(--crit); }

.peak { font-size: 12.5px; white-space: nowrap; }
.peak strong { font-size: 15px; font-weight: 800; color: var(--ink-strong); }
.spark { height: 110px; }

.docs-card .sub { white-space: normal; }
/* wide screens: the map grows to the height of the right-hand column */
@media (min-width: 1200px) {
  .home-grid { align-items: stretch; }
  .map-card { display: flex; flex-direction: column; }
  .map-card :deep(.map-wrap) { flex: 1; display: flex; flex-direction: column; }
  .map-card :deep(.map) { flex: 1; height: auto; min-height: 440px; }
}
/* five numbers: on phones the fifth spans the row (global rule) */
@media (min-width: 1024px) { .home-kpis .stat { flex-basis: 120px; } }
</style>
