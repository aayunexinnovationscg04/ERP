<template>
  <PageHeader title="Alerts" description="Fuel theft, tamper, geofence and driving events from your fleet. Acknowledge an alert once it has been handled.">
    <div class="seg" role="group" aria-label="Alert status">
      <button :class="{ on: filter === 'open' }" @click="setFilter('open')">Open</button>
      <button :class="{ on: filter === '' }" @click="setFilter('')">All</button>
    </div>
  </PageHeader>
  <p v-if="!canWrite" class="notice amber" style="margin:-4px 0 16px"><Lock :size="16" /> View only — you can see alerts but not acknowledge them.</p>

  <div v-if="loading && !alerts.length" class="kpis"><div class="skel sk-chip" v-for="n in 3" :key="n"></div></div>
  <div v-else class="kpis">
    <StatTile label="Critical" :value="criticalCount" :icon="Siren" tone="crit" />
    <StatTile label="Warning" :value="warningCount" :icon="TriangleAlert" tone="amber" />
    <StatTile label="Info" :value="infoCount" :icon="Info" tone="blue" />
  </div>

  <div class="card flush">
    <div class="card-head">
      <div class="chips" role="group" aria-label="Alert type">
        <button type="button" class="chip" :class="{ on: typeFilter === '' }" @click="typeFilter = ''">
          All types <span class="chip-count">{{ alerts.length }}</span>
        </button>
        <button type="button" class="chip" v-for="c in TYPE_CATEGORIES" :key="c.type" :class="{ on: typeFilter === c.type }"
                @click="typeFilter = typeFilter === c.type ? '' : c.type">
          <component :is="c.icon" :size="14" /> {{ c.label }}
          <span class="chip-count">{{ typeCounts[c.type] || 0 }}</span>
        </button>
      </div>
    </div>

    <div v-if="loading && !alerts.length" class="card-body"><div class="skel sk-row" v-for="n in 5" :key="n"></div></div>

    <EmptyState v-else-if="!filteredAlerts.length" :icon="ShieldCheck"
      :title="filter === 'open' ? 'No open alerts' : 'No alerts'"
      :text="typeFilter ? 'Nothing in this category.' : (filter === 'open' ? 'Everything has been handled. New events will appear here.' : 'Alerts from your vehicles will be listed here.')" />

    <template v-else>
      <div class="table-wrap hide-sm" :class="{ busy: loading }">
        <table>
          <thead>
            <tr><th>Alert</th><th>Severity</th><th>Vehicle</th><th>When</th><th class="num" style="width:150px">Status</th></tr>
          </thead>
          <tbody>
            <tr v-for="a in filteredAlerts" :key="a.id">
              <td>
                <div class="cell-with-icon">
                  <span class="icon-chip" :class="chipClass[a.severity]"><component :is="typeIcon(a.type)" :size="16" /></span>
                  <div style="min-width:0">
                    <div class="cell-main">{{ a.title }}</div>
                    <div class="cell-sub al-msg">{{ a.type_label || a.type }} · {{ a.message }}</div>
                  </div>
                </div>
              </td>
              <td><span class="badge" :class="a.severity">{{ a.severity }}</span></td>
              <td class="nowrap">{{ a.vehicle_reg || a.device_id || '—' }}</td>
              <td class="nowrap muted" :title="new Date(a.created_at).toLocaleString()">{{ ago(a.created_at) }}</td>
              <td class="num">
                <button v-if="a.status === 'open' && canWrite" class="sm" :disabled="acking === a.id" @click="ack(a)"><Check :size="14" /> Acknowledge</button>
                <span v-else class="badge plain" :class="a.status === 'open' ? 'critical' : 'offline'">{{ a.status }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="list show-sm">
        <div v-for="a in filteredAlerts" :key="a.id" class="list-row al-item">
          <span class="icon-chip" :class="chipClass[a.severity]"><component :is="typeIcon(a.type)" :size="16" /></span>
          <div class="grow">
            <div class="al-top"><span class="title">{{ a.title }}</span><span class="badge" :class="a.severity">{{ a.severity }}</span></div>
            <div class="al-body">{{ a.message }}</div>
            <div class="sub">{{ a.vehicle_reg || a.device_id || '—' }} · {{ ago(a.created_at) }}</div>
            <div class="al-actions">
              <button v-if="a.status === 'open' && canWrite" class="sm" :disabled="acking === a.id" @click="ack(a)"><Check :size="14" /> Acknowledge</button>
              <span v-else class="badge plain" :class="a.status === 'open' ? 'critical' : 'offline'">{{ a.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { Lock, TriangleAlert, Info, Gauge, MapPin, Fuel, ShieldAlert, ShieldCheck, Siren, WifiOff, Wrench, PauseCircle, Check } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import { getAlerts, ackAlert } from '../api'
import { auth } from '../auth'
import { ago } from '../util'
import { toast } from '../toast'

const canWrite = computed(() => auth.user?.may_write !== false)
const alerts = ref([])
const filter = ref('open')
const loading = ref(true)
const chipClass = { critical: 'crit', warning: 'amber', info: 'blue' }
const acking = ref(null)

// Every alert already carries a real category (type) beyond its severity —
// use it to vary the row's icon, not just its color, so a critical overspeed
// row doesn't look identical to a critical fuel-theft row.
const TYPE_ICON = {
  overspeed: Gauge,
  geofence_breach: MapPin,
  low_fuel: Fuel,
  fuel_fill: Fuel,
  fuel_theft: ShieldAlert,
  tamper: Siren,
  device_offline: WifiOff,
  sensor_fault: Wrench,
  idle_too_long: PauseCircle,
}
function typeIcon(type) { return TYPE_ICON[type] || TriangleAlert }

// Category filter chips — the app's scope note calls out five categories
// specifically (Fuel Theft / Low Fuel / Geo Security / Tamper / Overspeed).
// These map straight onto types the alert model already carries; no new
// alert type is invented here, just a lightweight client-side filter on top
// of whatever `load()` already fetched for the current status tab.
const TYPE_CATEGORIES = [
  { type: 'fuel_theft', label: 'Fuel Theft', icon: ShieldAlert },
  { type: 'low_fuel', label: 'Low Fuel', icon: Fuel },
  { type: 'geofence_breach', label: 'Geo Security', icon: MapPin },
  { type: 'tamper', label: 'Tamper', icon: Siren },
  { type: 'overspeed', label: 'Overspeed', icon: Gauge },
]
const typeFilter = ref('')
const filteredAlerts = computed(() =>
  typeFilter.value ? alerts.value.filter((a) => a.type === typeFilter.value) : alerts.value)
const typeCounts = computed(() => {
  const counts = {}
  for (const a of alerts.value) counts[a.type] = (counts[a.type] || 0) + 1
  return counts
})

const criticalCount = computed(() => filteredAlerts.value.filter((a) => a.severity === 'critical').length)
const warningCount = computed(() => filteredAlerts.value.filter((a) => a.severity === 'warning').length)
const infoCount = computed(() => filteredAlerts.value.filter((a) => a.severity === 'info').length)

async function load() {
  loading.value = true
  try { alerts.value = await getAlerts(filter.value ? { status: filter.value } : {}) }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
function setFilter(f) { filter.value = f; load() }
async function ack(a) {
  acking.value = a.id
  try {
    await ackAlert(a.id)
    toast.success('Alert acknowledged')
    await load()
  } catch (e) { toast.error('Could not acknowledge alert') }
  finally { acking.value = null }
}

onMounted(load)
</script>
<style scoped>
.card-head .chips { flex: 1; }
.al-msg { max-width: 520px; white-space: normal; }
.busy { opacity: .6; transition: opacity var(--dur) var(--ease); }
.al-item { align-items: flex-start; }
.al-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; }
.al-top .title { white-space: normal; }
.al-body { font-size: 13px; color: var(--text); margin: 2px 0 4px; }
.al-actions { margin-top: 10px; }
</style>
