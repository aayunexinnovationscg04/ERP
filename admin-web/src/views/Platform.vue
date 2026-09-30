<template>
  <PageHeader :icon="Activity" title="Platform Health" description="Service status, telemetry ingest and platform-wide totals. Refreshes every 30 seconds.">
    <span class="ph-meta" v-if="h"><Clock :size="13" /> Checked {{ fmtTime(h.time) }}</span>
    <button type="button" class="btn" :disabled="refreshing" @click="refresh"><RefreshCw :size="16" :class="{ spin: refreshing }" /> Refresh</button>
  </PageHeader>

  <div v-if="error && h" class="notice warn"><TriangleAlert :size="16" /> <span>Couldn't refresh. Showing the last check from {{ fmtTime(h.time) }}.</span></div>
  <div v-if="error && !h && !loading" class="card"><EmptyState :icon="ServerCrash" title="Health check unavailable" text="The platform health endpoint did not respond."><button type="button" class="btn" @click="refresh"><RefreshCw :size="16" /> Try again</button></EmptyState></div>

  <template v-else>
    <!-- status row -->
    <div class="health-row">
      <div class="card health-card" :class="!h ? '' : h.status === 'ok' ? 'ok' : 'bad'">
        <span class="hc-icon"><component :is="!h || h.status === 'ok' ? ShieldCheck : ShieldAlert" :size="20" /></span>
        <div>
          <div class="hc-label">Overall status</div>
          <div v-if="!h" class="skel skel-line md"></div>
          <div v-else class="hc-value">{{ h.status === 'ok' ? 'All systems operational' : 'Degraded' }}</div>
        </div>
      </div>
      <div class="card health-card" :class="!h ? '' : h.database?.ok ? 'ok' : 'bad'">
        <span class="hc-icon"><Database :size="20" /></span>
        <div>
          <div class="hc-label">Database</div>
          <div v-if="!h" class="skel skel-line md"></div>
          <div v-else class="hc-value">{{ h.database?.ok ? 'Connected' : 'Unreachable' }}<span v-if="h.database?.engine" class="hc-sub"> · {{ h.database.engine }}</span></div>
        </div>
      </div>
      <div class="card health-card" :class="!h ? '' : h.ingest?.stale ? 'warn' : 'ok'">
        <span class="hc-icon"><Radio :size="20" /></span>
        <div style="min-width:0">
          <div class="hc-label">Telemetry ingest</div>
          <div v-if="!h" class="skel skel-line md"></div>
          <div v-else class="hc-value">{{ h.ingest?.stale ? 'Stale' : 'Receiving data' }}<span class="hc-sub"> · {{ h.ingest?.last_received_at ? relTime(h.ingest.last_received_at) : 'no data yet' }}</span></div>
        </div>
      </div>
    </div>

    <div class="grid-main-side">
      <section class="card">
        <div class="card-head"><h2>Telemetry ingest</h2></div>
        <div class="card-body">
          <div v-if="!h"><div class="skel skel-row" v-for="n in 3" :key="n" style="margin-bottom:14px"></div></div>
          <template v-else>
            <div class="ingest-nums">
              <div><div class="stat-label">Last hour</div><div class="stat-value">{{ fmt(h.ingest?.records_last_hour) }}</div></div>
              <div><div class="stat-label">Last 24 hours</div><div class="stat-value">{{ fmt(h.ingest?.records_last_24h) }}</div></div>
              <div><div class="stat-label">All time</div><div class="stat-value">{{ fmt(c.telemetry_total) }}</div></div>
            </div>
            <div class="kv" style="margin-top:18px;padding-top:14px;border-top:1px solid var(--border)"><span class="k">Last reporting device</span><span class="v mono">{{ h.ingest?.last_device || '—' }}</span></div>
            <div class="kv"><span class="k">Last record received</span><span class="v">{{ h.ingest?.last_received_at ? fmtDateTime(h.ingest.last_received_at) : '—' }}</span></div>
          </template>
        </div>
      </section>

      <section class="card">
        <div class="card-head"><h2>Utilization</h2></div>
        <div class="card-body">
          <div v-if="!h"><div class="skel skel-row" v-for="n in 2" :key="n" style="margin-bottom:18px"></div></div>
          <template v-else>
            <div class="meter">
              <div class="meter-head"><span class="meter-label">Devices online</span><span class="meter-val">{{ devMeter.total ? devMeter.pct + '%' : '—' }}</span></div>
              <div class="bar-track"><span class="bar-fill" :style="{ width: devMeter.pct + '%', background: 'var(--info)' }"></span></div>
              <div class="meter-sub">{{ devMeter.total ? `${fmt(devMeter.online)} of ${fmt(devMeter.total)} devices` : 'No devices registered' }}</div>
            </div>
            <div class="meter">
              <div class="meter-head"><span class="meter-label">Trips in progress</span><span class="meter-val">{{ fmt(tripMeter.active) }}</span></div>
              <div class="bar-track"><span class="bar-fill" :style="{ width: tripMeter.pct + '%', background: 'var(--info)' }"></span></div>
              <div class="meter-sub">{{ tripMeter.total ? `${fmt(tripMeter.active)} active of ${fmt(tripMeter.total)} trips recorded` : 'No trips recorded' }}</div>
            </div>
          </template>
        </div>
      </section>
    </div>

    <p class="section-label">Platform totals</p>
    <div class="stats six">
      <StatCard label="Companies" :value="fmt(c.companies)" :icon="Building2" tone="navy" :loading="!h" />
      <StatCard label="Users" :value="fmt(c.users)" :icon="Users" tone="info" :loading="!h" />
      <StatCard label="Vehicles" :value="fmt(c.vehicles)" :icon="Truck" tone="teal" :loading="!h" />
      <StatCard label="Devices" :value="fmt(c.devices_total)" :icon="Cpu" tone="navy" :loading="!h" />
      <StatCard label="Trips recorded" :value="fmt(c.trips_total)" :icon="Route" tone="info" :loading="!h" />
      <StatCard label="Open alerts" :value="fmt(c.open_alerts)" :icon="Siren" :tone="c.open_alerts ? 'crit' : 'green'" :loading="!h" />
    </div>

    <section class="card">
      <div class="card-head"><h2>Users by role</h2></div>
      <div class="card-body">
        <div v-if="!h" class="bars"><div class="skel skel-row" v-for="n in 4" :key="n"></div></div>
        <EmptyState v-else-if="!hasRoleData" :icon="Users" title="No users yet" />
        <div v-else class="bars">
          <div v-for="d in roleData" :key="d.key" class="bar-row">
            <span class="bar-label"><span class="sw" :style="{ background: roleVar(d.key) }"></span>{{ d.label }}</span>
            <div class="bar-track"><span class="bar-fill" :style="{ width: barPct(d.count) + '%', background: roleVar(d.key) }"></span></div>
            <span class="bar-val">{{ d.count }}</span>
          </div>
        </div>
      </div>
    </section>
  </template>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import {
  Activity, Database, Radio, Clock, RefreshCw, TriangleAlert, ShieldCheck, ShieldAlert, ServerCrash,
  Building2, Users, Truck, Cpu, Route, Siren,
} from 'lucide-vue-next'
import { getHealth } from '../api'
import { fmt, fmtTime, fmtDateTime, relTime } from '../format'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'

const roleVarMap = { admin: 'var(--role-admin)', dealer: 'var(--role-dealer)', manager: 'var(--role-manager)', pilot: 'var(--role-pilot)' }
const roleVar = (key) => roleVarMap[key] || 'var(--info)'

const h = ref(null)
const loading = ref(true)
const refreshing = ref(false)
const error = ref(false)
let timer = null

const c = computed(() => h.value?.counts || {})
const roleData = computed(() => {
  const r = h.value?.counts?.users_by_role || {}
  return [
    { key: 'dealer', label: 'Dealer' }, { key: 'manager', label: 'Manager' },
    { key: 'pilot', label: 'Pilot' }, { key: 'admin', label: 'Admin' },
  ].map((o) => ({ ...o, count: Number(r[o.key] ?? 0) }))
})
const roleMax = computed(() => Math.max(1, ...roleData.value.map((d) => d.count)))
const hasRoleData = computed(() => roleData.value.some((d) => d.count > 0))
const barPct = (n) => (n ? (n / roleMax.value) * 100 : 0)
const devMeter = computed(() => {
  const online = Number(c.value.devices_online ?? 0); const total = Number(c.value.devices_total ?? 0)
  return { online, total, pct: total ? Math.round((online / total) * 100) : 0 }
})
const tripMeter = computed(() => {
  const active = Number(c.value.trips_active ?? 0); const total = Number(c.value.trips_total ?? 0)
  return { active, total, pct: total ? Math.round((active / total) * 100) : 0 }
})

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
async function refresh() { refreshing.value = true; await load(); refreshing.value = false }
onMounted(() => { load(); timer = setInterval(load, 30000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .8s linear infinite; }
.health-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin-bottom: 16px; }
.health-card { display: flex; align-items: center; gap: 14px; padding: 16px; min-width: 0; }
.hc-icon { width: 40px; height: 40px; border-radius: var(--radius-sm); display: grid; place-items: center; flex: none; background: var(--surface-3); color: var(--muted); }
.health-card.ok .hc-icon { background: var(--green-soft); color: var(--green); }
.health-card.warn .hc-icon { background: var(--amber-soft); color: var(--amber); }
.health-card.bad .hc-icon { background: var(--red-soft); color: var(--red); }
.health-card.bad { border-color: var(--red); }
.hc-label { font-size: .75rem; font-weight: 650; color: var(--muted); }
.hc-value { font-size: .95rem; font-weight: 750; color: var(--ink-strong); }
.hc-sub { font-weight: 500; color: var(--muted); font-size: .8125rem; }
.ingest-nums { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.ingest-nums > div + div { border-left: 1px solid var(--border); padding-left: 16px; }
.section-label { margin-top: 26px; }
.grid-main-side + .section-label { margin-top: 26px; }
@media (max-width: 1100px) { .health-row { grid-template-columns: minmax(0, 1fr); } }
@media (max-width: 480px) {
  .ingest-nums { grid-template-columns: minmax(0, 1fr); gap: 12px; }
  .ingest-nums > div + div { border-left: 0; padding-left: 0; border-top: 1px solid var(--border); padding-top: 12px; }
}
</style>
