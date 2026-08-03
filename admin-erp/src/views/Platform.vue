<template>
  <div class="platform">
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Systems</span>
      <h1 class="ico"><Activity :size="20" /> Platform Health</h1>
    </div>
    <div class="row">
      <span class="muted" style="font-size:12px">{{ h ? 'Updated ' + when(h.time) : '' }}</span>
    </div>
  </div>

  <!-- status banner -->
  <div v-if="loading && !h" class="card" style="padding:16px;margin-bottom:16px">
    <div class="skel skel-line md" style="margin:0"></div>
  </div>
  <div v-else-if="h" class="card banner" :class="h.status === 'ok' ? 'ok' : 'bad'">
    <span class="badge ico" :class="h.status === 'ok' ? 'active' : 'critical'">
      <component :is="h.status === 'ok' ? CircleCheck : CircleAlert" :size="15" />
      {{ h.status === 'ok' ? 'Operational' : 'Degraded' }}
    </span>
    <span class="badge ico" :class="h.database?.ok ? 'active' : 'offline'">
      <Database :size="14" /> Database: {{ h.database?.ok ? 'OK' : 'Down' }}
      <template v-if="h.database?.engine"> · {{ h.database.engine }}</template>
    </span>
    <div class="spacer"></div>
  </div>

  <!-- ingest -->
  <p class="section-title">Telemetry ingest</p>
  <div v-if="loading && !h" class="stats" style="margin-bottom:20px">
    <div class="card stat" v-for="n in 3" :key="n"><div class="skel skel-line lg"></div><div class="skel skel-line sm"></div></div>
  </div>
  <div v-else-if="h" class="card" style="padding:16px;margin-bottom:20px">
    <div class="row" style="flex-wrap:wrap;gap:14px">
      <div>
        <div class="l ico"><Radio :size="14" /> Last device</div>
        <div class="v">{{ h.ingest?.last_device || '—' }}</div>
        <div class="sub">{{ h.ingest?.last_received_at ? when(h.ingest.last_received_at) : 'No telemetry yet' }}</div>
      </div>
      <div class="spacer"></div>
      <span class="badge ico" :class="h.ingest?.stale ? 'warning' : 'active'">
        <component :is="h.ingest?.stale ? Clock : CircleCheck" :size="14" />
        {{ h.ingest?.stale ? 'Stale' : 'Live' }}
      </span>
    </div>
    <div class="stats" style="margin-top:16px">
      <div class="stat" style="padding:0">
        <div class="n">{{ fmt(h.ingest?.records_last_hour) }}</div>
        <div class="l">Records / last hour</div>
      </div>
      <div class="stat" style="padding:0">
        <div class="n">{{ fmt(h.ingest?.records_last_24h) }}</div>
        <div class="l">Records / last 24h</div>
      </div>
    </div>
  </div>

  <!-- counts -->
  <p class="section-title">Platform counts</p>
  <div v-if="loading && !h" class="stats">
    <div class="card stat" v-for="n in 8" :key="n"><div class="skel skel-line lg"></div><div class="skel skel-line sm"></div></div>
  </div>
  <div v-else-if="h" class="stats">
    <div class="card stat">
      <div class="n">{{ fmt(c.companies) }}</div><div class="l">Companies</div>
    </div>
    <div class="card stat">
      <div class="n">{{ fmt(c.users) }}</div><div class="l">Users</div>
      <div class="sub">{{ roleBreakdown }}</div>
    </div>
    <div class="card stat">
      <div class="n">{{ fmt(c.devices_online) }} <span class="muted" style="font-size:16px">/ {{ fmt(c.devices_total) }}</span></div>
      <div class="l">Devices online</div>
    </div>
    <div class="card stat">
      <div class="n">{{ fmt(c.vehicles) }}</div><div class="l">Vehicles</div>
    </div>
    <div class="card stat">
      <div class="n">{{ fmt(c.telemetry_total) }}</div><div class="l">Telemetry records</div>
    </div>
    <div class="card stat">
      <div class="n">{{ fmt(c.trips_active) }} <span class="muted" style="font-size:16px">/ {{ fmt(c.trips_total) }}</span></div>
      <div class="l">Active trips</div>
    </div>
    <div class="card stat">
      <div class="n">{{ fmt(c.open_alerts) }}</div><div class="l">Open alerts</div>
    </div>
  </div>

  <!-- distribution & utilization (monochrome inline-SVG viz) -->
  <div v-if="loading && !h" class="grid-2" style="margin-top:20px">
    <div class="card" style="padding:16px">
      <div class="skel skel-line md"></div>
      <div class="skel sk-row" v-for="n in 4" :key="n"></div>
    </div>
    <div class="card" style="padding:16px">
      <div class="skel skel-line md"></div>
      <div class="skel sk-row" v-for="n in 2" :key="n"></div>
    </div>
  </div>
  <div v-else-if="h" class="grid-2" style="margin-top:20px">
    <!-- users by role: horizontal bars, near-black on a muted track -->
    <div class="card" style="padding:16px">
      <p class="section-title" style="margin-bottom:14px">Users by role</p>
      <div v-if="hasRoleData" class="barchart">
        <div class="brow" v-for="d in roleData" :key="d.key">
          <span class="blabel">{{ d.label }}</span>
          <svg class="btrack" width="100%" height="12" role="img" :aria-label="`${d.label}: ${d.count} ${d.count === 1 ? 'user' : 'users'}`">
            <rect width="100%" height="12" rx="3" fill="var(--surface-2)" />
            <rect :width="barPct(d.count) + '%'" height="12" rx="3" fill="var(--brand)" />
          </svg>
          <span class="bval">{{ d.count }}</span>
        </div>
      </div>
      <div v-else class="empty">No users yet</div>
    </div>

    <!-- utilization: progress meters (filled = online / active) -->
    <div class="card" style="padding:16px">
      <p class="section-title" style="margin-bottom:14px">Utilization</p>
      <div class="meter">
        <div class="mhead">
          <span class="mlabel">Devices online</span>
          <span class="mval" v-if="devMeter.total">{{ fmt(devMeter.online) }} / {{ fmt(devMeter.total) }}</span>
          <span class="mval muted" v-else>None</span>
        </div>
        <svg class="btrack" width="100%" height="12" role="img"
             :aria-label="`Devices online ${devMeter.online} of ${devMeter.total}`">
          <rect width="100%" height="12" rx="3" fill="var(--surface-2)" />
          <rect :width="devMeter.pct + '%'" height="12" rx="3" fill="var(--brand)" />
        </svg>
        <div class="msub muted">{{ devMeter.total ? devMeter.pct + '% online' : 'No devices registered' }}</div>
      </div>
      <div class="meter" style="margin-top:18px">
        <div class="mhead">
          <span class="mlabel">Active trips</span>
          <span class="mval" v-if="tripMeter.total">{{ fmt(tripMeter.active) }} / {{ fmt(tripMeter.total) }}</span>
          <span class="mval muted" v-else>None</span>
        </div>
        <svg class="btrack" width="100%" height="12" role="img"
             :aria-label="`Active trips ${tripMeter.active} of ${tripMeter.total}`">
          <rect width="100%" height="12" rx="3" fill="var(--surface-2)" />
          <rect :width="tripMeter.pct + '%'" height="12" rx="3" fill="var(--brand)" />
        </svg>
        <div class="msub muted">{{ tripMeter.total ? tripMeter.pct + '% active' : 'No trips recorded' }}</div>
      </div>
    </div>
  </div>

  <div v-if="error" class="muted" style="margin-top:14px;font-size:12px">Could not refresh — showing last known data.</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Activity, Database, Radio, Clock, CircleCheck, CircleAlert } from 'lucide-vue-next'
import { getHealth } from '../api'

const h = ref(null)
const loading = ref(true)
const error = ref(false)
let timer = null

const c = computed(() => h.value?.counts || {})
const roleBreakdown = computed(() => {
  const r = h.value?.counts?.users_by_role
  if (!r) return ''
  return `${r.dealer ?? 0} dealer · ${r.manager ?? 0} mgr · ${r.pilot ?? 0} pilot · ${r.admin ?? 0} admin`
})

const rolesOrder = [
  { key: 'dealer', label: 'Dealer' },
  { key: 'manager', label: 'Manager' },
  { key: 'pilot', label: 'Pilot' },
  { key: 'admin', label: 'Admin' },
]
const roleData = computed(() => {
  const r = h.value?.counts?.users_by_role || {}
  return rolesOrder.map((o) => ({ ...o, count: Number(r[o.key] ?? 0) }))
})
const roleMax = computed(() => Math.max(1, ...roleData.value.map((d) => d.count)))
const hasRoleData = computed(() => roleData.value.some((d) => d.count > 0))
function barPct(n) {
  if (!n) return 0
  return Math.max(6, (n / roleMax.value) * 100)   // floor so a small non-zero bar stays visible
}
const devMeter = computed(() => {
  const online = Number(c.value.devices_online ?? 0)
  const total = Number(c.value.devices_total ?? 0)
  return { online, total, pct: total ? Math.round((online / total) * 100) : 0 }
})
const tripMeter = computed(() => {
  const active = Number(c.value.trips_active ?? 0)
  const total = Number(c.value.trips_total ?? 0)
  return { active, total, pct: total ? Math.round((active / total) * 100) : 0 }
})

function fmt(n) { return n == null ? '—' : Number(n).toLocaleString() }
function when(s) { return s ? new Date(s).toLocaleString() : '—' }

async function load() {
  try {
    h.value = await getHealth()
    error.value = false
  } catch (e) {
    error.value = true   // keep last good data
  } finally {
    loading.value = false
  }
}

onMounted(() => { load(); timer = setInterval(load, 30000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.banner { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding: 14px 16px; }
.banner.ok { border-left: 3px solid var(--green); }
.banner.bad { border-left: 3px solid var(--red); }
.l { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .05em; font-weight: 700; }
.v { font-size: 18px; font-weight: 800; margin-top: 4px; letter-spacing: -.01em; }
.sub { color: var(--muted); font-size: 12px; margin-top: 3px; }

/* users-by-role bar chart */
.barchart { display: flex; flex-direction: column; gap: 13px; }
.brow { display: grid; grid-template-columns: 74px 1fr 32px; align-items: center; gap: 12px; }
.blabel { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.bval { font-size: 13px; font-weight: 800; text-align: right; font-variant-numeric: tabular-nums; }
.btrack { display: block; }
.empty { color: var(--muted); font-size: 13px; text-align: center; padding: 16px 0; }

/* utilization meters */
.meter .mhead { display: flex; justify-content: space-between; align-items: baseline; gap: 8px; margin-bottom: 8px; }
.mlabel { font-size: 12px; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
.mval { font-size: 14px; font-weight: 800; font-variant-numeric: tabular-nums; }
.msub { font-size: 11px; margin-top: 6px; }
</style>
