<template>
  <div class="topbar">
    <h1 class="ico"><Activity :size="20" /> Platform Health</h1>
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

  <div v-if="error" class="muted" style="margin-top:14px;font-size:12px">Could not refresh — showing last known data.</div>
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
  return `${r.owner ?? 0} owner · ${r.manager ?? 0} mgr · ${r.driver ?? 0} driver · ${r.superadmin ?? 0} admin`
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
</style>
