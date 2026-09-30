<template>
  <PageHeader :title="v ? v.local_name : 'Vehicle'" :back="{ to: '/fuel', label: 'Fuel Overview' }">
    <template #description>
      <span v-if="v">{{ v.registration_number }} · last reading {{ ago(latest?.received_at) }}</span><span v-else>&nbsp;</span>
    </template>
    <router-link v-if="v" :to="`/vehicles/${v.id}`" class="btn"><Truck :size="16" /> Vehicle profile</router-link>
  </PageHeader>

  <div v-if="loading">
    <div class="kpis"><div class="skel sk-chip" v-for="n in 4" :key="n"></div></div>
    <div class="skel sk-hero"></div>
  </div>

  <EmptyState v-else-if="!v" class="card" :icon="Fuel" title="Vehicle not found">
    <router-link to="/fuel" class="btn">Back to fuel overview</router-link>
  </EmptyState>

  <template v-else>
    <div class="card fd-hero">
      <div class="fd-hero-main">
        <span class="icon-chip lg brand"><Fuel :size="20" /></span>
        <div>
          <div class="kpi-label">Current fuel level</div>
          <div class="fd-value num" v-if="latest?.total_litres != null">{{ fmt(latest.total_litres) }} <small>L</small></div>
          <div class="fd-value fd-none" v-else>No reading yet</div>
        </div>
        <div v-if="v.tank_capacity_litres && latest?.total_litres != null" class="fd-pct">
          <b class="num">{{ pctFull }}%</b><span>of {{ v.tank_capacity_litres }} L tank</span>
        </div>
      </div>
      <div v-if="v.tank_capacity_litres" class="meter fd-meter"><span :class="pctFull <= 15 ? 'crit' : pctFull <= 40 ? 'amber' : 'green'" :style="{ width: pctFull + '%' }"></span></div>
      <p v-else class="muted" style="font-size:12.5px;margin-top:8px">Tank capacity not set</p>
    </div>

    <div class="kpis section">
      <StatTile label="Consumed" :value="fmt(totalConsumed)" unit="L" :icon="Droplet" tone="brand" />
      <StatTile label="Distance" :value="fmt(totalDistance, 0)" unit="km" :icon="Milestone" tone="navy" />
      <StatTile label="Efficiency" :value="efficiencyKmpl != null ? fmt(efficiencyKmpl) : '—'" :unit="efficiencyKmpl != null ? 'km/L' : ''" :icon="TrendingUp" tone="green" />
      <StatTile label="Completed trips" :value="completedTrips.length" :icon="RouteIcon" tone="blue" />
    </div>

    <div class="card">
      <div class="card-head"><div class="card-head-title"><Activity :size="17" /><h2>Fuel level trend</h2></div></div>
      <div class="card-body">
        <template v-if="trend">
          <svg class="spark" :viewBox="`0 0 ${trend.width} ${trend.height}`" preserveAspectRatio="none"
               role="img" aria-label="Fuel level trend over recent telemetry">
            <line :x1="0" :y1="trend.base" :x2="trend.width" :y2="trend.base" stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
            <polyline :points="trend.area" fill="var(--brand)" fill-opacity="0.12" stroke="none" />
            <polyline :points="trend.line" fill="none" stroke="var(--brand)" stroke-width="2"
                      stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
          </svg>
          <div class="legend-row">
            <span>Oldest <b>{{ fmt(litresSeries[0]) }}</b> L</span>
            <span>Latest <b>{{ fmt(litresSeries[litresSeries.length - 1]) }}</b> L</span>
          </div>
        </template>
        <EmptyState v-else compact :icon="Activity" title="Not enough readings yet" />
      </div>
    </div>

    <div class="grid-2-even section">
      <div class="card flush">
        <div class="card-head"><div class="card-head-title"><CirclePlus :size="17" /><h2>Refill log</h2></div>
          <span class="badge info plain">{{ refills.length }}</span></div>
        <div v-if="refills.length" class="table-wrap">
          <table class="mstack">
            <thead><tr><th>When</th><th class="num">Added</th><th>Note</th></tr></thead>
            <tbody>
              <tr v-for="a in refillPager.rows.value" :key="a.id">
                <td data-label="When" class="nowrap">{{ dt(a.created_at) }}</td>
                <td data-label="Added" class="num" style="color:var(--green);font-weight:700">{{ a.meta?.delta_litres != null ? '+' + fmt(a.meta.delta_litres) + ' L' : '—' }}</td>
                <td data-label="Note" class="muted cell-full">{{ a.message }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager v-if="refills.length" :pager="refillPager" />
        <EmptyState v-else compact :icon="CirclePlus" title="No refills recorded yet" />
      </div>

      <div class="card flush">
        <div class="card-head"><div class="card-head-title"><ShieldAlert :size="17" /><h2>Fuel theft alerts</h2></div>
          <span class="badge plain" :class="thefts.length ? 'critical' : 'offline'">{{ thefts.length }}</span></div>
        <div v-if="thefts.length" class="table-wrap">
          <table class="mstack">
            <thead><tr><th>Alert</th><th>When</th><th class="num">Lost</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-for="a in theftPager.rows.value" :key="a.id">
                <td class="cell-head cell-main">{{ a.title }}</td>
                <td data-label="When" class="nowrap">{{ dt(a.created_at) }}</td>
                <td data-label="Lost" class="num" style="color:var(--crit);font-weight:700">{{ a.meta?.delta_litres != null ? '−' + fmt(Math.abs(a.meta.delta_litres)) + ' L' : '—' }}</td>
                <td data-label="Status"><span class="badge" :class="a.status === 'open' ? 'critical' : 'offline'">{{ a.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager v-if="thefts.length" :pager="theftPager" />
        <EmptyState v-else compact :icon="ShieldCheck" title="No theft alerts on file" />
      </div>
    </div>
  </template>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  Fuel, Truck, Droplet, Milestone, TrendingUp, Route as RouteIcon, Activity, CirclePlus, ShieldAlert, ShieldCheck,
} from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { getVehicle, getVehicleTrack, getVehicleTrips, getAlerts } from '../api'
import { fmt, ago, sparkline } from '../util'

const props = defineProps({ id: [String, Number] })
const v = ref(null)
const track = ref([])
const trips = ref([])
const refills = ref([])
const thefts = ref([])
const loading = ref(true)
const dt = (iso) => new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })

const refillPager = usePaging(refills, 10)
const theftPager = usePaging(thefts, 10)
const latest = computed(() => v.value?.latest)
const pctFull = computed(() => {
  if (!v.value?.tank_capacity_litres || latest.value?.total_litres == null) return 0
  return Math.max(0, Math.min(100, Math.round((latest.value.total_litres / v.value.tank_capacity_litres) * 100)))
})

const completedTrips = computed(() => trips.value.filter((t) => t.status === 'completed'))
const tripsWithFuel = computed(() => completedTrips.value.filter((t) => t.fuel_consumed_litres > 0))
const totalConsumed = computed(() => completedTrips.value.reduce((s, t) => s + (t.fuel_consumed_litres || 0), 0))
const totalDistance = computed(() => completedTrips.value.reduce((s, t) => s + (t.distance_km || 0), 0))
const efficiencyKmpl = computed(() => {
  const dist = tripsWithFuel.value.reduce((s, t) => s + (t.distance_km || 0), 0)
  const fuel = tripsWithFuel.value.reduce((s, t) => s + (t.fuel_consumed_litres || 0), 0)
  return fuel > 0 ? dist / fuel : null
})

const litresSeries = computed(() => track.value.map((p) => Number(p.total_litres)).filter((n) => Number.isFinite(n)))
const trend = computed(() => sparkline(litresSeries.value))

async function load() {
  try {
    v.value = await getVehicle(props.id)
    ;[track.value, trips.value, refills.value, thefts.value] = await Promise.all([
      getVehicleTrack(props.id, 1000),
      getVehicleTrips(props.id),
      getAlerts({ vehicle: props.id, type: 'fuel_fill' }),
      getAlerts({ vehicle: props.id, type: 'fuel_theft' }),
    ])
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(load)
</script>
<style scoped>
.fd-hero { padding: 14px 18px; margin-bottom: 12px; }
.kpis.section, .section { margin-top: 12px; }
.fd-hero-main { display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
.fd-value { font-family: var(--font-head); font-size: 28px; font-weight: 800; letter-spacing: -.02em; color: var(--ink-strong); line-height: 1.1; }
.fd-value small { font-size: 16px; color: var(--muted); font-weight: 700; }
.fd-none { font-size: 22px; color: var(--muted); }
.fd-pct { margin-left: auto; text-align: right; display: flex; flex-direction: column; }
.fd-pct b { font-size: 20px; color: var(--ink-strong); }
.fd-pct span { font-size: 12.5px; color: var(--muted); }
.fd-meter { height: 10px; margin-top: 12px; }
@media (max-width: 720px) { .fd-hero { padding: 12px 14px; } .fd-value { font-size: 24px; } }
@media (max-width: 480px) { .fd-pct { margin-left: 0; text-align: left; width: 100%; flex-direction: row; gap: 8px; align-items: baseline; } }
</style>
