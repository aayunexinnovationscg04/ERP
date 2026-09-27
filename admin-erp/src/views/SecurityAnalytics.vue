<template>
  <PageHeader :icon="ShieldAlert" title="Fraud & Theft Alerts" description="Alerts raised by the detection engine across every company: fuel theft, tampering, geofence breaches and more.">
    <span class="ph-meta" v-if="fetchedAt"><Clock :size="13" /> Updated {{ fmtTime(fetchedAt) }}</span>
    <button type="button" class="btn" :disabled="refreshing" @click="refresh"><RefreshCw :size="16" :class="{ spin: refreshing }" /> Refresh</button>
  </PageHeader>

  <div class="stats">
    <StatCard label="Open alerts" :value="fmt(openCount)" :icon="Siren" :tone="openCount ? 'crit' : 'green'" :loading="loading" />
    <StatCard label="Critical, open" :value="fmt(critOpen)" :icon="OctagonAlert" :tone="critOpen ? 'red' : 'navy'" :loading="loading" />
    <StatCard label="Fuel theft & tamper" :value="fmt(theftCount)" :icon="Fuel" :tone="theftCount ? 'amber' : 'navy'" :loading="loading" sub="All statuses" />
    <StatCard label="Acknowledged / resolved" :value="fmt(alerts.length - openCount)" :icon="CircleCheck" tone="green" :loading="loading" />
  </div>

  <div class="grid-main-side sec-grid">
    <section class="card">
      <div class="toolbar">
        <label class="input-icon">
          <Search :size="16" />
          <input v-model="q" class="input" type="search" placeholder="Search alerts or vehicles" aria-label="Search alerts" />
        </label>
        <div class="seg" role="group" aria-label="Filter by status">
          <button v-for="f in statusFilters" :key="f.key" type="button" :class="{ on: status === f.key }" @click="status = f.key">
            {{ f.label }} <span class="count">{{ f.count }}</span>
          </button>
        </div>
        <select v-model="severity" class="select" aria-label="Filter by severity">
          <option value="">All severities</option>
          <option value="critical">Critical</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
      </div>
      <div class="table-wrap">
        <table class="table stack alerts-table">
          <thead><tr><th>Alert</th><th>Severity</th><th>Vehicle</th><th>Status</th><th>Raised</th></tr></thead>
          <TableSkeleton v-if="loading" :cols="5" :rows="6" />
          <tbody v-else-if="loadError">
            <tr class="table-empty"><td colspan="5"><EmptyState :icon="CircleAlert" title="Alerts could not be loaded"><button type="button" class="btn" @click="refresh">Try again</button></EmptyState></td></tr>
          </tbody>
          <tbody v-else-if="!filtered.length">
            <tr class="table-empty"><td colspan="5">
              <EmptyState v-if="!alerts.length" :icon="ShieldCheck" title="No alerts raised" text="Nothing has been flagged across the platform." />
              <EmptyState v-else :icon="Search" title="No matching alerts" text="Try a different search or filter." />
            </td></tr>
          </tbody>
          <tbody v-else>
            <tr v-for="a in pagedRows" :key="a.id">
              <td class="cell-head">
                <div class="alert-cell">
                  <span class="type-ic" :class="a.severity"><component :is="typeIcon(a.type)" :size="16" /></span>
                  <div style="min-width:0">
                    <div class="t-primary">{{ a.title }}</div>
                    <div class="t-secondary">{{ a.type_label }}<template v-if="a.message"> · {{ a.message }}</template></div>
                  </div>
                </div>
              </td>
              <td data-label="Severity"><span class="badge" :class="sevClass(a.severity)"><span class="bdot"></span>{{ cap(a.severity) }}</span></td>
              <td data-label="Vehicle" class="mono nowrap">{{ a.vehicle_reg || a.device_id || '—' }}</td>
              <td data-label="Status"><span class="status-dot" :class="a.status === 'open' ? 'red' : a.status === 'acknowledged' ? 'amber' : 'green'">{{ cap(a.status) }}</span></td>
              <td data-label="Raised" class="nowrap muted" :title="fmtDateTime(a.created_at)">{{ relTime(a.created_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <Pager :pager="pager" />
    </section>

    <div class="vstack">
      <section class="card">
        <div class="card-head"><div><h2>Last 7 days</h2><div class="sub">Alerts raised per day</div></div><span v-if="!loading" class="t-primary num">{{ weekTotal }}</span></div>
        <div class="card-body">
          <div v-if="loading" class="skel skel-block"></div>
          <div v-else class="cols" role="img" :aria-label="days.map((d) => `${d.label}: ${d.count}`).join(', ')">
            <div v-for="d in days" :key="d.key" class="col" :title="`${d.full}: ${d.count} alert${d.count === 1 ? '' : 's'}`">
              <span class="col-val num">{{ d.count || '' }}</span>
              <div class="col-bar"><span :style="{ height: (d.count / dayMax * 100) + '%' }"></span></div>
              <span class="col-lbl">{{ d.label }}</span>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <div class="card-head"><div><h2>By type</h2><div class="sub">All alerts on record</div></div></div>
        <div class="card-body">
          <div v-if="loading" class="bars"><div class="skel skel-row" v-for="n in 4" :key="n"></div></div>
          <EmptyState v-else-if="!byType.length" :icon="ShieldCheck" title="No alerts yet" />
          <div v-else class="bars">
            <div v-for="t in byType" :key="t.type" class="bar-row">
              <span class="bar-label" :title="t.label">{{ t.label }}</span>
              <div class="bar-track"><span class="bar-fill" :style="{ width: (t.count / typeMax * 100) + '%' }"></span></div>
              <span class="bar-val">{{ t.count }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  ShieldAlert, ShieldCheck, Siren, OctagonAlert, Fuel, CircleCheck, CircleAlert, Search, Clock, RefreshCw,
  Gauge, MapPinOff, FuelIcon, Wrench, WifiOff, Unplug, CirclePause, TriangleAlert,
} from 'lucide-vue-next'
import { getAlerts } from '../api'
import { fmt, fmtTime, fmtDateTime, relTime } from '../format'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import TableSkeleton from '../components/TableSkeleton.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const alerts = ref([])
const loading = ref(true)
const refreshing = ref(false)
const loadError = ref(false)
const fetchedAt = ref(null)
const q = ref('')
const status = ref('open')
const severity = ref('')

const typeIcons = {
  overspeed: Gauge, geofence_breach: MapPinOff, low_fuel: Fuel, fuel_fill: FuelIcon, fuel_theft: Fuel,
  tamper: Unplug, device_offline: WifiOff, sensor_fault: Wrench, idle_too_long: CirclePause,
}
const typeIcon = (t) => typeIcons[t] || TriangleAlert
const sevClass = (s) => (s === 'critical' ? 'critical' : s === 'warning' ? 'warning' : 'info')
const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : '—')
const sevRank = { critical: 0, warning: 1, info: 2 }

const openCount = computed(() => alerts.value.filter((a) => a.status === 'open').length)
const critOpen = computed(() => alerts.value.filter((a) => a.status === 'open' && a.severity === 'critical').length)
const theftCount = computed(() => alerts.value.filter((a) => a.type === 'fuel_theft' || a.type === 'tamper').length)
const statusFilters = computed(() => [
  { key: 'open', label: 'Open', count: openCount.value },
  { key: 'closed', label: 'Handled', count: alerts.value.length - openCount.value },
  { key: 'all', label: 'All', count: alerts.value.length },
])
const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  return alerts.value
    .filter((a) => status.value === 'all' || (status.value === 'open' ? a.status === 'open' : a.status !== 'open'))
    .filter((a) => !severity.value || a.severity === severity.value)
    .filter((a) => !term || [a.title, a.message, a.vehicle_reg, a.device_id, a.type_label].some((f) => (f || '').toLowerCase().includes(term)))
    .sort((x, y) => (sevRank[x.severity] ?? 3) - (sevRank[y.severity] ?? 3) || new Date(y.created_at) - new Date(x.created_at))
})

const byType = computed(() => {
  const m = {}
  alerts.value.forEach((a) => { (m[a.type] ||= { type: a.type, label: a.type_label || a.type, count: 0 }).count++ })
  return Object.values(m).sort((a, b) => b.count - a.count)
})
const typeMax = computed(() => Math.max(1, ...byType.value.map((t) => t.count)))

const days = computed(() => {
  const out = []
  const today = new Date(); today.setHours(0, 0, 0, 0)
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today); d.setDate(d.getDate() - i)
    const next = new Date(d); next.setDate(next.getDate() + 1)
    const count = alerts.value.filter((a) => { const t = new Date(a.created_at); return t >= d && t < next }).length
    out.push({
      key: d.toISOString(), count,
      label: i === 0 ? 'Today' : d.toLocaleDateString(undefined, { weekday: 'short' }),
      full: d.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'short' }),
    })
  }
  return out
})
const dayMax = computed(() => Math.max(1, ...days.value.map((d) => d.count)))
const weekTotal = computed(() => days.value.reduce((s, d) => s + d.count, 0))

async function load() {
  try {
    alerts.value = await getAlerts()
    fetchedAt.value = new Date()
    loadError.value = false
  } catch (e) {
    loadError.value = !alerts.value.length
  } finally { loading.value = false }
}
async function refresh() { refreshing.value = true; await load(); refreshing.value = false }
onMounted(load)

// pagination (resets to page 1 when search/filters change)
const pager = usePaging(filtered)
const pagedRows = pager.rows
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .8s linear infinite; }
.alert-cell { display: flex; gap: 11px; align-items: flex-start; min-width: 240px; }
.alert-cell .t-secondary { max-width: 46ch; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; white-space: normal; }
.type-ic { width: 32px; height: 32px; border-radius: var(--radius-sm); flex: none; display: grid; place-items: center; background: var(--info-soft); color: var(--info); }
.type-ic.warning { background: var(--amber-soft); color: var(--amber); }
.type-ic.critical { background: var(--crit-soft); color: var(--crit); }
.cols { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 8px; height: 150px; }
.col { display: flex; flex-direction: column; align-items: center; gap: 6px; min-width: 0; }
.col-val { font-size: .75rem; font-weight: 750; color: var(--ink-strong); height: 16px; }
.col-bar { flex: 1; width: 100%; max-width: 28px; display: flex; align-items: flex-end; background: var(--surface-3); border-radius: 4px; overflow: hidden; }
.col-bar span { display: block; width: 100%; background: var(--crit); border-radius: 4px 4px 0 0; min-height: 0; }
.col-lbl { font-size: .72rem; color: var(--muted); white-space: nowrap; }
@media (max-width: 1360px) {
  .sec-grid { grid-template-columns: minmax(0, 1fr); }
  .sec-grid > .vstack { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; }
}
@media (max-width: 720px) {
  .sec-grid > .vstack { grid-template-columns: minmax(0, 1fr); }
  .alert-cell { min-width: 0; }
  .alerts-table .toolbar .select { flex-basis: 100%; }
}
</style>
