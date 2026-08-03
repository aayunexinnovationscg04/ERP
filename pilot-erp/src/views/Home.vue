<template>
  <div v-if="loading">
    <div class="skel sk-hero"></div>
    <div class="chips">
      <div class="skel sk-chip"></div><div class="skel sk-chip"></div>
      <div class="skel sk-chip"></div><div class="skel sk-chip"></div>
    </div>
    <div class="section-title"><div class="skel skel-line sm" style="margin:0"></div></div>
    <div class="skel sk-map"></div>
  </div>

  <div v-else-if="!assigned" class="card empty">
    <Truck :size="42" :stroke-width="1.5" style="color:var(--muted)" />
    <h2 style="margin:10px 0 6px">No truck assigned yet</h2>
    <p class="muted">Your dispatcher hasn't linked a vehicle to your account.<br />Once they do, it shows up here.</p>
  </div>

  <div v-else>
    <!-- status hero -->
    <div class="card hero">
      <div class="row">
        <div>
          <div class="reg">{{ v.registration_number }}</div>
          <div class="sub">{{ [v.make, v.model].filter(Boolean).join(' ') || 'Vehicle' }}</div>
        </div>
        <div class="spacer"></div>
        <div style="text-align:right">
          <span class="badge" :class="v.status">{{ v.status }}</span>
          <div style="margin-top:8px">
            <span class="badge" :class="summary.on_trip ? 'on' : 'off'">
              {{ summary.on_trip ? '● On trip' : 'Parked' }}
            </span>
          </div>
        </div>
      </div>

      <div class="chips">
        <div class="chip"><div class="l">Speed</div><div class="v ico"><Gauge :size="18" /> {{ fmt(latest?.speed_kmph) }} <small class="muted">km/h</small></div></div>
        <div class="chip"><div class="l">Distance today</div><div class="v ico"><Milestone :size="18" /> {{ summary.distance_today_km ?? 0 }} <small class="muted">km</small></div></div>
        <div class="chip"><div class="l">Fuel cap</div><div class="v ico"><component :is="latest?.lock_active ? Lock : LockOpen" :size="18" /> {{ latest?.lock_active ? 'Locked' : 'Open' }}</div></div>
        <div class="chip"><div class="l">GPS</div><div class="v ico"><Satellite :size="18" /> {{ latest?.has_gps_fix ? ((latest?.satellites ?? 0) + ' sats') : 'No fix' }}</div></div>
      </div>
    </div>

    <!-- speed data viz -->
    <div v-if="spark" class="card viz-card">
      <div class="viz-head">
        <span class="l">Speed — last {{ spark.n }} points</span>
        <span class="spacer"></span>
        <span class="m">max {{ spark.max }} km/h</span>
      </div>
      <div class="viz-body">
        <div v-if="gauge" class="gauge">
          <svg viewBox="0 0 120 66" width="112" height="62" role="img"
               :aria-label="`Current speed ${gauge.speed} km/h out of 60 km/h reference`">
            <path :d="gauge.track" fill="none" stroke="var(--surface-2)" stroke-width="9" stroke-linecap="round" />
            <path :d="gauge.val" fill="none" stroke="var(--brand)" stroke-width="9" stroke-linecap="round" />
            <text x="60" y="52" text-anchor="middle" font-size="22" font-weight="800" fill="var(--text)">{{ gauge.speed }}</text>
            <text x="60" y="63" text-anchor="middle" font-size="9" fill="var(--muted)">km/h · ref 60</text>
          </svg>
        </div>
        <svg class="spark" :viewBox="`0 0 ${spark.w} ${spark.h}`" preserveAspectRatio="none"
             role="img" :aria-label="`Speed over the last ${spark.n} readings, currently ${spark.last} km/h, peak ${spark.max} km/h`">
          <polyline :points="spark.area" fill="var(--brand)" fill-opacity=".10" stroke="none" />
          <line x1="0" :y1="spark.base" :x2="spark.w" :y2="spark.base" stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
          <polyline :points="spark.line" fill="none" stroke="var(--brand)" stroke-width="1.5"
                    stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
        </svg>
      </div>
    </div>

    <div v-if="summary.open_alerts" class="card item" style="border-color:var(--crit)">
      <div><div class="t ico"><Bell :size="16" /> {{ summary.open_alerts }} open alert{{ summary.open_alerts > 1 ? 's' : '' }}</div>
        <div class="d">Tap the Alerts tab to review</div></div>
      <router-link to="/alerts" class="badge critical" style="align-self:center">View</router-link>
    </div>

    <div class="section-title">Live location &amp; today's route</div>
    <FleetMap :markers="markers" :track="track" />

    <div class="muted" style="font-size:12px; margin-top:12px; text-align:center">
      Last update: {{ latest ? new Date(latest.received_at).toLocaleString() : '—' }} · refreshes every 20s
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Truck, Gauge, Milestone, Lock, LockOpen, Satellite, Bell } from 'lucide-vue-next'
import FleetMap from '../components/FleetMap.vue'
import { getSummary, getMyTrack } from '../api'

const loading = ref(true)
const summary = ref({})
const track = ref([])
const speeds = ref([])
let timer = null

const assigned = computed(() => summary.value.assigned)
const v = computed(() => summary.value.vehicle || {})
const latest = computed(() => summary.value.latest)

const markers = computed(() => {
  const l = latest.value
  if (!l || !l.has_gps_fix) return []
  return [{ id: v.value.id, lat: l.latitude, lng: l.longitude, label: v.value.registration_number, status: v.value.status }]
})

function fmt(n) { return n == null ? '—' : Math.round(n) }

// speed sparkline (inline SVG, brand-colored, built from recent telemetry)
const spark = computed(() => {
  const arr = speeds.value.slice(-60)
  if (arr.length < 2) return null
  const w = 300, h = 90, pad = 8
  const max = Math.max(...arr), min = Math.min(...arr)
  const range = (max - min) || 1
  const n = arr.length
  const X = (i) => pad + (i / (n - 1)) * (w - pad * 2)
  const Y = (val) => pad + (1 - (val - min) / range) * (h - pad * 2)
  const line = arr.map((val, i) => `${X(i).toFixed(1)},${Y(val).toFixed(1)}`).join(' ')
  const base = (h - pad).toFixed(1)
  const area = `${X(0).toFixed(1)},${base} ${line} ${X(n - 1).toFixed(1)},${base}`
  return { line, area, w, h, base, n, max: Math.round(max), last: Math.round(arr[n - 1]) }
})

// speed gauge (SVG arc) — current speed vs a 60 km/h reference
const gauge = computed(() => {
  const s = latest.value?.speed_kmph
  if (s == null) return null
  const cx = 60, cy = 44, r = 40
  const pct = Math.max(0, Math.min(1, s / 60))
  const polar = (deg) => {
    const a = (deg * Math.PI) / 180
    return [cx + r * Math.cos(a), cy - r * Math.sin(a)]
  }
  const arc = (endDeg) => {
    const [x1, y1] = polar(180)
    const [x2, y2] = polar(endDeg)
    return `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 0 0 ${x2.toFixed(1)} ${y2.toFixed(1)}`
  }
  return { track: arc(0), val: arc(180 - pct * 180), speed: Math.round(s) }
})

async function load() {
  try {
    summary.value = await getSummary()
    if (summary.value.assigned) {
      const pts = await getMyTrack(500)
      track.value = pts.filter((p) => p.has_gps_fix).map((p) => [p.latitude, p.longitude])
      speeds.value = pts.filter((p) => p.speed_kmph != null).map((p) => p.speed_kmph)
    }
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}

onMounted(() => { load(); timer = setInterval(load, 20000) })
onBeforeUnmount(() => clearInterval(timer))
</script>
