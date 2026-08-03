<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Global Fleet Monitoring</span>
      <h1 class="ico"><Radar :size="20" /> Fleet Overview</h1>
    </div>
    <span class="muted" style="font-size:12px">{{ s ? 'Updated ' + when(fetchedAt) : '' }}</span>
  </div>
  <p class="hint">Cross-company vehicle and device connectivity, live from the platform dashboard aggregate.</p>

  <div v-if="loading && !s" class="stats">
    <div class="card stat" v-for="n in 6" :key="n"><div class="skel skel-line lg"></div><div class="skel skel-line sm"></div></div>
  </div>
  <div v-else-if="s" class="stats">
    <div class="card stat" :style="statStyle('violet')">
      <span class="stat-icon"><Truck :size="16" /></span>
      <div class="n">{{ fmt(s.vehicles_total) }}</div><div class="l">Total vehicles</div>
    </div>
    <div class="card stat" :style="statStyle('green')">
      <span class="stat-icon"><CircleCheck :size="16" /></span>
      <div class="n">{{ fmt(s.active) }}</div><div class="l">Active</div>
    </div>
    <div class="card stat" :style="statStyle('amber')">
      <span class="stat-icon"><Clock :size="16" /></span>
      <div class="n">{{ fmt(s.idle) }}</div><div class="l">Idle</div>
    </div>
    <div class="card stat" :style="statStyle(s.offline > 0 ? 'rose' : 'green')">
      <span class="stat-icon"><WifiOff :size="16" /></span>
      <div class="n">{{ fmt(s.offline) }}</div><div class="l">Offline</div>
    </div>
    <div class="card stat" :style="statStyle(devPct >= 60 ? 'green' : 'amber')">
      <span class="stat-icon"><Wifi :size="16" /></span>
      <div class="n">{{ fmt(s.devices_online) }} <span class="muted" style="font-size:16px">/ {{ fmt(s.devices_total) }}</span></div>
      <div class="l">Devices online</div>
    </div>
    <div class="card stat" :style="statStyle(s.open_alerts > 0 ? 'rose' : 'green')">
      <span class="stat-icon"><TriangleAlert :size="16" /></span>
      <div class="n">{{ fmt(s.open_alerts) }}</div><div class="l">Open alerts</div>
    </div>
  </div>

  <div v-if="s" class="grid-2" style="margin-top:20px">
    <div class="card" style="padding:16px">
      <p class="section-title" style="margin-bottom:14px">Fleet status split</p>
      <div class="barchart">
        <div class="brow" v-for="d in statusRows" :key="d.key">
          <span class="blabel" :style="{ color: d.color }">{{ d.label }}</span>
          <svg class="btrack" width="100%" height="12" role="img" :aria-label="`${d.label}: ${d.count}`">
            <rect width="100%" height="12" rx="3" fill="var(--surface-3)" />
            <rect :width="statusPct(d.count) + '%'" height="12" rx="3" :fill="d.color" />
          </svg>
          <span class="bval">{{ d.count }}</span>
        </div>
      </div>
    </div>
    <div class="card" style="padding:16px">
      <p class="section-title" style="margin-bottom:14px">Today across the platform</p>
      <div class="row" style="justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border)">
        <span class="muted">Distance covered</span><span style="font-weight:800">{{ fmt(s.distance_today_km) }} km</span>
      </div>
      <div class="row" style="justify-content:space-between;padding:8px 0">
        <span class="muted">Fuel consumed</span><span style="font-weight:800">{{ fmt(s.fuel_today_litres) }} L</span>
      </div>
      <div class="meter" style="margin-top:16px">
        <div class="mhead">
          <span class="mlabel">Device connectivity</span>
          <span class="mval">{{ devPct }}%</span>
        </div>
        <svg class="btrack" width="100%" height="12" role="img" :aria-label="`Devices online ${devPct}%`">
          <rect width="100%" height="12" rx="3" fill="var(--surface-3)" />
          <rect :width="devPct + '%'" height="12" rx="3" fill="var(--brand)" />
        </svg>
      </div>
    </div>
  </div>

  <div v-if="error" class="muted" style="margin-top:14px;font-size:12px">Could not refresh — showing last known data.</div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { Radar, Truck, CircleCheck, Clock, WifiOff, Wifi, TriangleAlert } from 'lucide-vue-next'
import { getFleetSummary } from '../api'

const statColors = {
  violet: ['#8b5cf6', 'rgba(139,92,246,.16)'],
  green: ['#22c55e', 'rgba(34,197,94,.16)'],
  amber: ['#f59e0b', 'rgba(245,158,11,.16)'],
  rose: ['#f43f5e', 'rgba(244,63,94,.16)'],
}
function statStyle(name) {
  const [c, soft] = statColors[name] || statColors.violet
  return { '--stat-color': c, '--stat-color-soft': soft }
}

const s = ref(null)
const loading = ref(true)
const error = ref(false)
const fetchedAt = ref(null)
let timer = null

const devPct = computed(() => {
  if (!s.value?.devices_total) return 0
  return Math.round((s.value.devices_online / s.value.devices_total) * 100)
})
const statusRows = computed(() => {
  if (!s.value) return []
  return [
    { key: 'active', label: 'Active', count: s.value.active, color: 'var(--green)' },
    { key: 'idle', label: 'Idle', count: s.value.idle, color: 'var(--amber)' },
    { key: 'offline', label: 'Offline', count: s.value.offline, color: 'var(--slate)' },
  ]
})
const statusMax = computed(() => Math.max(1, ...statusRows.value.map((d) => d.count)))
function statusPct(n) { return n ? Math.max(6, (n / statusMax.value) * 100) : 0 }

function fmt(n) { return n == null ? '—' : Number(n).toLocaleString() }
function when(d) { return d ? d.toLocaleTimeString() : '—' }

async function load() {
  try {
    s.value = await getFleetSummary()
    fetchedAt.value = new Date()
    error.value = false
  } catch (e) {
    error.value = true
  } finally {
    loading.value = false
  }
}
onMounted(() => { load(); timer = setInterval(load, 30000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.barchart { display: flex; flex-direction: column; gap: 13px; }
.brow { display: grid; grid-template-columns: 60px 1fr 32px; align-items: center; gap: 12px; }
.blabel { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; }
.bval { font-size: 13px; font-weight: 800; text-align: right; font-variant-numeric: tabular-nums; }
.btrack { display: block; }
.meter .mhead { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin-bottom: 8px; }
.mlabel { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.mval { font-size: 14px; font-weight: 800; font-variant-numeric: tabular-nums; }
</style>
