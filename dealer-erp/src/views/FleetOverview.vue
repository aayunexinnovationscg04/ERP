<template>
  <PageHeader title="Fleet Overview"
    :description="companyName ? `Live status of every vehicle at ${companyName}.` : 'Live status of every vehicle in your fleet.'">
    <router-link to="/locations" class="btn"><LocateFixed :size="16" /> Live map</router-link>
    <router-link to="/vehicles" class="btn primary"><Truck :size="16" /> All vehicles</router-link>
  </PageHeader>

  <div v-if="loading" class="kpis"><div class="skel sk-chip" v-for="n in 5" :key="n"></div></div>
  <div v-else class="kpis">
    <StatTile label="Total vehicles" :value="vehicles.length" :icon="Truck" tone="navy" to="/vehicles"
      :sub="withGps + ' reporting GPS'" />
    <StatTile label="Active" :value="counts.active" :icon="Navigation" tone="green" :sub="pctOf(counts.active)" />
    <StatTile label="Idle" :value="counts.idle" :icon="PauseCircle" tone="amber" :sub="pctOf(counts.idle)" />
    <StatTile label="Offline" :value="counts.offline" :icon="WifiOff" tone="gray" :sub="pctOf(counts.offline)" />
    <StatTile label="Open alerts" :value="alerts.length" :icon="ShieldAlert" tone="crit" to="/alerts"
      :sub="critCount ? `${critCount} critical` : 'None critical'" />
  </div>

  <div v-if="!loading && !vehicles.length" class="card">
    <EmptyState :icon="Truck" title="No vehicles yet"
      text="Vehicles appear here once your Aayunex administrator installs a Fuel Guard X device and links it to your company." />
  </div>

  <template v-else>
    <div class="grid-2">
      <div class="card flush">
        <div class="card-head">
          <div class="card-head-title"><LocateFixed :size="17" /><div><h2>Live fleet map</h2>
            <div class="card-sub">{{ markers.length }} of {{ vehicles.length }} vehicles with a GPS fix</div></div></div>
          <div class="map-legend">
            <span><i class="swatch" style="background:#059669"></i>Active</span>
            <span><i class="swatch" style="background:#D97706"></i>Idle</span>
            <span><i class="swatch" style="background:#64748B"></i>Offline</span>
          </div>
        </div>
        <div v-if="loading" class="skel" style="height:420px;border-radius:0"></div>
        <FleetMap v-else :markers="markers" height="420px" @select="(id) => $router.push(`/vehicles/${id}`)" />
      </div>

      <div class="stack">
        <div class="card">
          <div class="card-head">
            <div class="card-head-title"><HeartPulse :size="17" /><h2>Fleet health</h2></div>
          </div>
          <div class="card-body fo-health">
            <svg class="fo-donut" viewBox="0 0 120 120" role="img" aria-label="Fleet health breakdown">
              <circle cx="60" cy="60" r="46" fill="none" stroke="var(--surface-3)" stroke-width="14" />
              <circle v-for="seg in donutSegs" :key="seg.key" cx="60" cy="60" r="46" fill="none"
                      :stroke="seg.color" stroke-width="14"
                      :stroke-dasharray="`${seg.dash} ${circumference - seg.dash}`"
                      :stroke-dashoffset="seg.offset" transform="rotate(-90 60 60)" />
              <text x="60" y="58" text-anchor="middle" class="fo-donut-n">{{ vehicles.length }}</text>
              <text x="60" y="74" text-anchor="middle" class="fo-donut-l">vehicles</text>
            </svg>
            <div class="fo-legend">
              <div class="fo-legend-row" v-for="seg in healthDefs" :key="seg.key">
                <span class="swatch" :style="{ background: seg.color }"></span>
                <span class="fo-legend-label">{{ seg.label }}</span>
                <b class="num">{{ seg.count }}</b>
              </div>
            </div>
          </div>
          <div class="card-foot">Critical = expired document or in maintenance. Needs attention = document expiring within 30 days or vehicle offline.</div>
        </div>

        <div class="card">
          <div class="card-head">
            <div class="card-head-title"><Bell :size="17" /><h2>Open alerts</h2></div>
            <router-link to="/alerts" class="link-more">View all <ChevronRight :size="14" /></router-link>
          </div>
          <EmptyState v-if="!alerts.length" compact :icon="ShieldCheck" title="All clear" text="No open alerts right now." />
          <div v-else class="list">
            <router-link v-for="a in alerts.slice(0, 5)" :key="a.id" to="/alerts" class="list-row">
              <span class="icon-chip" :class="sevChip[a.severity] || 'gray'"><TriangleAlert :size="16" /></span>
              <span class="grow">
                <div class="title">{{ a.title }}</div>
                <div class="sub">{{ a.vehicle_reg || a.device_id || '—' }} · {{ ago(a.created_at) }}</div>
              </span>
              <span class="badge" :class="a.severity">{{ a.severity }}</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="card flush section">
      <div class="card-head">
        <div class="card-head-title"><Truck :size="17" /><div><h2>Vehicle roster</h2>
          <div class="card-sub">Refreshes every 30 seconds</div></div></div>
      </div>
      <div v-if="loading" class="card-body"><div class="skel sk-row" v-for="n in 5" :key="n"></div></div>
      <div v-else class="table-wrap hide-sm">
        <table>
          <thead><tr>
            <th>Vehicle</th><th>Status</th><th class="hide-sm">Pilot</th><th class="hide-sm num">Fuel</th>
            <th class="hide-sm">Last update</th><th>Health</th><th style="width:48px"></th>
          </tr></thead>
          <tbody>
            <tr v-for="v in roster" :key="v.id" class="clickable" @click="$router.push(`/vehicles/${v.id}`)">
              <td>
                <div class="cell-with-icon">
                  <span class="dot" :class="freshness(v)" :title="'Telemetry ' + ago(v.latest?.received_at)"></span>
                  <div><div class="cell-main">{{ v.local_name }}</div><div class="cell-sub">{{ v.registration_number }}</div></div>
                </div>
              </td>
              <td><span class="badge" :class="v.status">{{ v.status }}</span></td>
              <td class="hide-sm">{{ v.active_pilot?.name || '—' }}</td>
              <td class="hide-sm num">{{ v.latest?.total_litres != null ? fmt(v.latest.total_litres) + ' L' : '—' }}</td>
              <td class="hide-sm muted nowrap">{{ ago(v.latest?.received_at) }}</td>
              <td><span class="badge" :class="v.health.cls">{{ v.health.label }}</span></td>
              <td><router-link :to="`/vehicles/${v.id}`" class="row-link" title="Open vehicle" @click.stop><ChevronRight :size="17" /></router-link></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!loading" class="list show-sm">
        <router-link v-for="v in roster" :key="v.id" :to="`/vehicles/${v.id}`" class="list-row">
          <span class="dot" :class="freshness(v)"></span>
          <span class="grow">
            <div class="title">{{ v.local_name }}</div>
            <div class="sub">{{ v.registration_number }} · <span :style="{ color: v.health.key === 'good' ? 'var(--green)' : v.health.key === 'warning' ? 'var(--amber)' : 'var(--crit)', fontWeight: 600 }">{{ v.health.label }}</span></div>
          </span>
          <span class="badge" :class="v.status">{{ v.status }}</span>
        </router-link>
      </div>
    </div>
  </template>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  Truck, Navigation, PauseCircle, WifiOff, ShieldAlert, ShieldCheck, LocateFixed, HeartPulse, Bell,
  ChevronRight, TriangleAlert,
} from 'lucide-vue-next'
import { getVehicles, getAlerts } from '../api'
import { auth } from '../auth'
import { ago, fmt, freshness } from '../util'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import FleetMap from '../components/FleetMap.vue'

const companyName = computed(() => auth.user?.company?.name || '')
const vehicles = ref([])
const alerts = ref([])
const loading = ref(true)
let timer

const sevChip = { critical: 'crit', warning: 'amber', info: 'blue' }
const counts = computed(() => ({
  active: vehicles.value.filter((v) => v.status === 'active').length,
  idle: vehicles.value.filter((v) => v.status === 'idle' || v.status === 'maintenance').length,
  offline: vehicles.value.filter((v) => v.status === 'offline').length,
}))
const critCount = computed(() => alerts.value.filter((a) => a.severity === 'critical').length)
function pctOf(n) {
  return vehicles.value.length ? `${Math.round((n / vehicles.value.length) * 100)}% of fleet` : '—'
}

const markers = computed(() => vehicles.value
  .filter((v) => v.latest?.has_gps_fix && v.latest.latitude != null)
  .map((v) => ({ id: v.id, lat: v.latest.latitude, lng: v.latest.longitude, label: `${v.local_name} · ${v.registration_number}`, status: v.status, speed: v.latest.speed_kmph != null ? fmt(v.latest.speed_kmph, 0) : null })))
const withGps = computed(() => markers.value.length)

// Health derived from real signals: document expiry + vehicle status.
function healthOf(v) {
  const docs = v.documents || []
  if (v.status === 'maintenance') return { key: 'critical', label: 'In maintenance', cls: 'critical' }
  if (docs.some((d) => d.expiry_status === 'expired')) return { key: 'critical', label: 'Document expired', cls: 'critical' }
  if (v.status === 'offline') return { key: 'warning', label: 'Offline', cls: 'warning' }
  if (docs.some((d) => d.expiry_status === 'expiring_soon')) return { key: 'warning', label: 'Document expiring', cls: 'warning' }
  return { key: 'good', label: 'Good', cls: 'active' }
}
const roster = computed(() => vehicles.value.map((v) => ({ ...v, health: healthOf(v) })))
const healthDefs = computed(() => {
  const c = { good: 0, warning: 0, critical: 0 }
  roster.value.forEach((v) => { c[v.health.key]++ })
  return [
    { key: 'good', label: 'Good', count: c.good, color: 'var(--green)' },
    { key: 'warning', label: 'Needs attention', count: c.warning, color: 'var(--amber)' },
    { key: 'critical', label: 'Critical', count: c.critical, color: 'var(--crit)' },
  ]
})
const circumference = 2 * Math.PI * 46
const donutSegs = computed(() => {
  const total = vehicles.value.length || 1
  let acc = 0
  return healthDefs.value.filter((d) => d.count > 0).map((d) => {
    const dash = (d.count / total) * circumference
    const seg = { ...d, dash, offset: -acc }
    acc += dash
    return seg
  })
})

async function load() {
  try {
    const [v, a] = await Promise.all([getVehicles(), getAlerts({ status: 'open' })])
    vehicles.value = v
    alerts.value = a
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(() => { load(); timer = setInterval(load, 30000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.fo-health { display: flex; align-items: center; gap: 22px; flex-wrap: wrap; }
.fo-donut { width: 128px; height: 128px; flex: none; }
.fo-donut-n { fill: var(--ink-strong); font-size: 24px; font-weight: 800; font-family: var(--font-head); }
.fo-donut-l { fill: var(--muted); font-size: 9.5px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; }
.fo-legend { flex: 1; min-width: 160px; display: flex; flex-direction: column; gap: 10px; }
.fo-legend-row { display: flex; align-items: center; gap: 10px; font-size: 13.5px; }
.fo-legend-label { flex: 1; font-weight: 600; }
.fo-legend-row b { color: var(--ink-strong); font-size: 15px; }
</style>
