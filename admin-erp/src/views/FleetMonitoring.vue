<template>
  <PageHeader :icon="Radar" title="Fleet Overview" description="Vehicle status and device connectivity across every company. Refreshes every 30 seconds.">
    <span class="ph-meta" v-if="fetchedAt"><Clock :size="13" /> Updated {{ fmtTime(fetchedAt) }}</span>
    <button type="button" class="btn" :disabled="refreshing" @click="refresh"><RefreshCw :size="16" :class="{ spin: refreshing }" /> Refresh</button>
  </PageHeader>

  <div v-if="error && s" class="notice warn"><TriangleAlert :size="16" /> <span>Couldn't refresh. Showing the last data received at {{ fmtTime(fetchedAt) }}.</span></div>
  <div v-if="error && !s && !loading" class="card"><EmptyState :icon="WifiOff" title="Fleet data is unavailable" text="The platform summary could not be loaded."><button type="button" class="btn" @click="refresh"><RefreshCw :size="16" /> Try again</button></EmptyState></div>

  <template v-else>
    <div class="stats six">
      <StatCard label="Total vehicles" :value="fmt(s?.vehicles_total)" :icon="Truck" tone="navy" :loading="!s" />
      <StatCard label="Active" :value="fmt(s?.active)" :icon="Navigation" tone="green" :loading="!s" />
      <StatCard label="Idle" :value="fmt(s?.idle)" :icon="CirclePause" tone="amber" :loading="!s" />
      <StatCard label="Offline" :value="fmt(s?.offline)" :icon="WifiOff" :tone="s?.offline ? 'red' : 'navy'" :loading="!s" />
      <StatCard label="Devices online" :icon="Wifi" :tone="devPct >= 60 ? 'green' : 'amber'" :loading="!s" :sub="s ? devPct + '% connected' : ''">
        {{ fmt(s?.devices_online) }}<span class="of"> / {{ fmt(s?.devices_total) }}</span>
      </StatCard>
      <StatCard label="Open alerts" :value="fmt(s?.open_alerts)" :icon="Siren" :tone="s?.open_alerts ? 'crit' : 'green'" :loading="!s">
        <template #sub><router-link to="/security-analytics">Review alerts</router-link></template>
      </StatCard>
    </div>

    <div class="grid-2" style="align-items:start">
      <section class="card">
        <div class="card-head"><h2>Fleet status</h2></div>
        <div class="card-body">
          <div v-if="!s" class="skel skel-row"></div>
          <template v-else>
            <div class="stacked" role="img" :aria-label="statusRows.map((d) => `${d.label} ${d.count}`).join(', ')">
              <span v-for="d in statusRows" v-show="d.count" :key="d.key" :style="{ flex: d.count, background: d.color }" :title="`${d.label}: ${d.count}`"></span>
            </div>
            <div class="legend">
              <span v-for="d in statusRows" :key="d.key"><i :style="{ background: d.color }"></i>{{ d.label }} <b>{{ d.count }}</b> <span class="muted">({{ pctOf(d.count) }})</span></span>
            </div>
          </template>
        </div>
      </section>

      <section class="card">
        <div class="card-head"><h2>Last 24 hours</h2></div>
        <div class="card-body">
          <div v-if="!s"><div class="skel skel-row" v-for="n in 3" :key="n" style="margin-bottom:14px"></div></div>
          <template v-else>
            <div class="kv"><span class="k"><Route :size="16" /> Distance covered</span><span class="v">{{ fmt(s.distance_today_km) }} km</span></div>
            <div class="kv"><span class="k"><Fuel :size="16" /> Fuel consumed</span><span class="v">{{ fmt(s.fuel_today_litres) }} L</span></div>
            <div class="meter" style="margin-top:22px">
              <div class="meter-head"><span class="meter-label">Device connectivity</span><span class="meter-val">{{ devPct }}%</span></div>
              <div class="bar-track"><span class="bar-fill" :style="{ width: devPct + '%', background: 'var(--info)' }"></span></div>
              <div class="meter-sub">{{ fmt(s.devices_online) }} of {{ fmt(s.devices_total) }} devices reporting</div>
            </div>
          </template>
        </div>
      </section>
    </div>
  </template>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { Radar, Truck, Navigation, CirclePause, WifiOff, Wifi, Siren, Clock, RefreshCw, TriangleAlert, Route, Fuel } from 'lucide-vue-next'
import { getFleetSummary } from '../api'
import { fmt, fmtTime } from '../format'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'

const s = ref(null)
const loading = ref(true)
const refreshing = ref(false)
const error = ref(false)
const fetchedAt = ref(null)
let timer = null

const devPct = computed(() => (s.value?.devices_total ? Math.round((s.value.devices_online / s.value.devices_total) * 100) : 0))
const statusRows = computed(() => (!s.value ? [] : [
  { key: 'active', label: 'Active', count: s.value.active, color: 'var(--green)' },
  { key: 'idle', label: 'Idle', count: s.value.idle, color: 'var(--amber)' },
  { key: 'offline', label: 'Offline', count: s.value.offline, color: 'var(--slate)' },
  // the summary has no field for vehicles in maintenance; show the remainder
  ...(otherCount.value > 0 ? [{ key: 'other', label: 'Maintenance', count: otherCount.value, color: 'var(--info)' }] : []),
]))
const otherCount = computed(() => (s.value ? s.value.vehicles_total - s.value.active - s.value.idle - s.value.offline : 0))
const pctOf = (n) => (s.value?.vehicles_total ? Math.round((n / s.value.vehicles_total) * 100) + '%' : '0%')

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
async function refresh() { refreshing.value = true; await load(); refreshing.value = false }
onMounted(() => { load(); timer = setInterval(load, 30000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .8s linear infinite; }
</style>
