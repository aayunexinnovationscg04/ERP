<template>
  <div class="page-head">
    <div class="ph-text">
      <h1>My Truck</h1>
    </div>
    <div v-if="!loading && assigned" class="ph-actions">
      <button class="btn btn-sm" type="button" @click="refresh" :disabled="refreshing" aria-label="Refresh now">
        <RefreshCw :size="16" :stroke-width="2.25" :class="{ spin: refreshing }" /> Refresh
      </button>
    </div>
  </div>

  <!-- loading -->
  <div v-if="loading" class="home-grid">
    <div class="skel sk-hero" style="grid-area:hero"></div>
    <div class="skel sk-map" style="grid-area:map"></div>
  </div>

  <!-- no vehicle assigned -->
  <div v-else-if="!assigned" class="card empty-state">
    <span class="empty-ic"><Truck :size="34" :stroke-width="1.75" /></span>
    <h2>No truck assigned yet</h2>
    <p>Ask your fleet manager to link one.</p>
    <div class="empty-actions">
      <button class="btn btn-primary" type="button" @click="checkAgain" :disabled="refreshing">
        <RefreshCw :size="18" :stroke-width="2.25" :class="{ spin: refreshing }" /> Check again
      </button>
    </div>
  </div>

  <div v-else class="home-grid">
    <!-- vehicle status -->
    <motion.section class="card hero" style="grid-area:hero" aria-label="Vehicle status"
      :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }" :transition="pageTransition(reduced)">
      <div class="hero-top">
        <div class="hero-id">
          <span class="plate">{{ v.registration_number }}</span>
          <div class="hero-model">
            <span>{{ modelLine }}</span>
            <span class="badge" :class="v.status">{{ statusLabel(v.status) }}</span>
          </div>
        </div>
        <AnimatePresence mode="wait">
          <motion.span :key="summary.on_trip ? 'on' : 'off'" class="badge badge-lg" :class="summary.on_trip ? 'on' : 'off'"
            :initial="{ opacity: 0, scale: reduced ? 1 : 0.9 }" :animate="{ opacity: 1, scale: 1 }" :exit="{ opacity: 0 }"
            :transition="emphasisTransition(reduced)">
            <span class="dot"></span>{{ summary.on_trip ? 'On trip' : 'Parked' }}
          </motion.span>
        </AnimatePresence>
      </div>

      <div class="speed-block">
        <div class="speed-read">
          <span class="speed-num">{{ fmt(latest?.speed_kmph) }}</span>
          <span class="speed-unit">km/h</span>
        </div>
        <div class="speed-meta">
          <span class="muted">Current speed</span>
          <strong>{{ latest?.speed_kmph == null ? 'No reading' : latest.speed_kmph > 2 ? 'Moving' : 'Stopped' }}</strong>
        </div>
      </div>

      <div class="stat-grid">
        <div class="stat tone-info">
          <div class="stat-top"><span class="stat-ic"><Milestone :size="17" :stroke-width="2.25" /></span><span class="stat-label">Today</span></div>
          <div class="stat-value">{{ summary.distance_today_km ?? 0 }}<small>km</small></div>
        </div>
        <div class="stat" :class="latest?.lock_active ? 'tone-green' : 'tone-amber'">
          <div class="stat-top"><span class="stat-ic"><component :is="latest?.lock_active ? Lock : LockOpen" :size="17" :stroke-width="2.25" /></span><span class="stat-label">Fuel cap</span></div>
          <div class="stat-value sm">{{ latest ? (latest.lock_active ? 'Locked' : 'Open') : '—' }}</div>
        </div>
        <div class="stat" :class="latest?.has_gps_fix ? 'tone-green' : 'tone-amber'">
          <div class="stat-top"><span class="stat-ic"><Satellite :size="17" :stroke-width="2.25" /></span><span class="stat-label">GPS</span></div>
          <div class="stat-value sm">{{ latest?.has_gps_fix ? `${latest?.satellites ?? 0} sats` : 'No fix' }}</div>
        </div>
        <div class="stat" :class="trackerTone">
          <div class="stat-top"><span class="stat-ic"><RadioTower :size="17" :stroke-width="2.25" /></span><span class="stat-label">Tracker</span></div>
          <div class="stat-value sm">{{ trackerLabel }}</div>
        </div>
      </div>

      <div class="hero-foot">
        <span class="live-dot" :class="{ stale: isStale }" aria-hidden="true"></span>
        <span>Updated {{ latest ? timeAgo(latest.received_at, nowTick) : '—' }}</span>
      </div>
    </motion.section>

    <!-- open alerts -->
    <AnimatePresence>
      <motion.div v-if="summary.open_alerts" key="alert-banner" style="grid-area:alert"
        :initial="{ opacity: 0, y: reduced ? 0 : -6 }" :animate="{ opacity: 1, y: 0 }" :exit="{ opacity: 0 }"
        :transition="emphasisTransition(reduced)">
        <router-link to="/alerts" class="alert-banner">
          <span class="ab-ic"><ShieldAlert :size="22" :stroke-width="2.25" /></span>
          <span class="ab-text">
            <strong>{{ summary.open_alerts }} open alert{{ summary.open_alerts > 1 ? 's' : '' }}</strong>
          </span>
          <span class="ab-go">Review <ChevronRight :size="18" :stroke-width="2.5" /></span>
        </router-link>
      </motion.div>
    </AnimatePresence>

    <!-- live map -->
    <section class="card map-card map-area" style="grid-area:map" aria-label="Live location">
      <div class="card-head">
        <span class="ch-ic ic-info"><MapPin :size="18" :stroke-width="2.25" /></span>
        <div class="ch-text"><h2>Live location</h2></div>
      </div>
      <FleetMap :markers="markers" :track="track" empty-text="Waiting for a GPS fix" />
    </section>

    <!-- speed trend -->
    <section v-if="spark" class="card" style="grid-area:speed" aria-label="Speed trend">
      <div class="card-head">
        <span class="ch-ic ic-brand"><Gauge :size="18" :stroke-width="2.25" /></span>
        <div class="ch-text"><h2>Speed trend</h2></div>
        <div class="peak"><span class="muted">Peak</span> <strong class="num">{{ spark.max }}</strong> <span class="muted">km/h</span></div>
      </div>
      <div class="card-pad">
        <svg class="spark" :viewBox="`0 0 ${spark.w} ${spark.h}`" preserveAspectRatio="none" role="img"
          :aria-label="`Speed over the last ${spark.n} readings, currently ${spark.last} km/h, peak ${spark.max} km/h`">
          <line x1="0" :y1="spark.base" :x2="spark.w" :y2="spark.base" stroke="var(--border-strong)" stroke-width="1" vector-effect="non-scaling-stroke" />
          <polyline :points="spark.area" fill="var(--brand)" fill-opacity=".12" stroke="none" />
          <polyline :points="spark.line" fill="none" stroke="var(--brand)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
        </svg>
      </div>
    </section>

    <!-- documents -->
    <section v-if="docs.length" class="card" style="grid-area:docs" aria-label="Vehicle documents">
      <div class="card-head">
        <span class="ch-ic ic-neutral"><FileText :size="18" :stroke-width="2.25" /></span>
        <div class="ch-text"><h2>Documents</h2></div>
        <span v-if="docIssues" class="badge" :class="docsExpired ? 'expired' : 'expiring_soon'">{{ docIssues }} to renew</span>
        <span v-else class="badge valid">All valid</span>
      </div>
      <ul class="list">
        <li v-for="d in docs" :key="d.id" class="list-row">
          <span class="row-ic" :class="docTone(d.expiry_status)"><component :is="docIcon(d.expiry_status)" :size="19" :stroke-width="2.25" /></span>
          <div class="row-main">
            <div class="row-title">{{ d.doc_type_label }}</div>
            <div v-if="docSub(d)" class="row-sub">{{ docSub(d) }}</div>
          </div>
          <span class="badge" :class="d.expiry_status">{{ docStatusLabel(d.expiry_status) }}</span>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { motion, AnimatePresence } from 'motion-v'
import {
  Truck, Gauge, Milestone, Lock, LockOpen, Satellite, ShieldAlert, RefreshCw, MapPin,
  ChevronRight, RadioTower, FileText, FileCheck, FileClock, FileX,
} from 'lucide-vue-next'
import FleetMap from '../components/FleetMap.vue'
import { getSummary, getMyTrack, getMyVehicle } from '../api'
import { toast } from '../toast'
import { timeAgo, shortDate } from '../format'
import { usePrefersReducedMotion, pageTransition, emphasisTransition } from '../motion'

const reduced = usePrefersReducedMotion()
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
const trackerTone = computed(() => (!device.value ? '' : device.value.online ? 'tone-green' : 'tone-red'))

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
function docTone(s) { return s === 'expired' ? 'ic-red' : s === 'expiring_soon' ? 'ic-amber' : 'ic-green' }
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
.home-grid {
  display: grid; gap: 14px; grid-template-columns: minmax(0, 1fr);
  grid-template-areas: "hero" "alert" "map" "speed" "docs";
}
@media (min-width: 1100px) {
  .home-grid {
    grid-template-columns: minmax(0, 5fr) minmax(0, 6fr); gap: 18px; align-items: start;
    grid-template-areas: "hero map" "alert map" "speed map" "docs docs";
  }
  .home-grid > .map-area { align-self: stretch; display: flex; flex-direction: column; }
  .home-grid > .map-area :deep(.map-wrap) { flex: 1; display: flex; flex-direction: column; }
  .home-grid > .map-area :deep(.map) { flex: 1; min-height: 420px; }
}

.hero { padding: 18px; display: flex; flex-direction: column; gap: 16px; }
.hero-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.hero-id { min-width: 0; }
/* Indian number-plate styling: white plate, dark border, heavy letters */
.plate {
  display: inline-block; max-width: 100%; padding: 5px 12px; border-radius: var(--radius-xs);
  background: #FFFFFF; color: var(--navy-900); border: 2px solid var(--navy-900);
  font-size: 1.375rem; font-weight: 800; letter-spacing: .06em; line-height: 1.2;
  font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
:root[data-theme="dark"] .plate { border-color: #CBD5E1; }
.hero-model { display: flex; align-items: center; flex-wrap: wrap; gap: 6px 10px; color: var(--muted); font-size: .9375rem; font-weight: 600; margin-top: 10px; }

.speed-block {
  display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; flex-wrap: wrap;
  padding: 14px 16px; border-radius: var(--radius); background: var(--surface-2); border: 1px solid var(--border);
}
.speed-read { display: flex; align-items: baseline; gap: 8px; }
.speed-num { font-size: 3.5rem; font-weight: 800; letter-spacing: -.04em; line-height: 1; color: var(--ink-strong); font-variant-numeric: tabular-nums; }
.speed-unit { font-size: 1.125rem; font-weight: 700; color: var(--muted); }
.speed-meta { display: flex; flex-direction: column; align-items: flex-end; gap: 2px; font-size: .8125rem; font-weight: 600; }
.speed-meta strong { font-size: 1rem; color: var(--ink-strong); }

.hero-foot { display: flex; align-items: center; gap: 8px; font-size: .8125rem; font-weight: 600; color: var(--text); }
.live-dot { width: 9px; height: 9px; border-radius: 50%; background: var(--green); flex: none; }
.live-dot.stale { background: var(--amber); }

.alert-banner {
  display: flex; align-items: center; gap: 14px; min-height: 72px; padding: 14px 16px;
  border-radius: var(--radius); background: var(--crit-soft); border: 1px solid var(--crit);
  color: var(--text); text-decoration: none;
}
.alert-banner:hover { border-color: var(--crit-strong); }
.ab-ic { flex: none; width: 44px; height: 44px; border-radius: var(--radius); display: grid; place-items: center; background: var(--crit); color: #FFFFFF; }
:root[data-theme="dark"] .ab-ic { background: var(--crit-strong); }
.ab-text { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.ab-text strong { font-size: 1rem; font-weight: 800; color: var(--ink-strong); }
.ab-text span { font-size: .8125rem; color: var(--muted); }
.ab-go { flex: none; display: inline-flex; align-items: center; gap: 2px; font-weight: 800; color: var(--crit); font-size: .9375rem; }

.peak { font-size: .8125rem; white-space: nowrap; }
.peak strong { font-size: 1.125rem; font-weight: 800; color: var(--ink-strong); }
.spark { display: block; width: 100%; height: 110px; }

@media (min-width: 600px) and (max-width: 1099.98px) { .hero .stat-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
.spin { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 380px) {
  .plate { font-size: 1.1875rem; }
  .speed-num { font-size: 3rem; }
  .card-head .badge { display: none; }
}
</style>
