<template>
  <div class="topbar">
    <div class="row" style="gap:12px">
      <button type="button" class="back-btn" @click="$router.back()" title="Back">
        <ArrowLeft :size="17" />
      </button>
      <h1><router-link to="/fuel" class="muted">Fuel</router-link> / {{ v?.local_name || '…' }}</h1>
    </div>
  </div>

  <div v-if="loading" class="card" style="padding:16px">
    <div class="skel skel-line lg"></div>
    <div class="skel skel-line md"></div>
    <div class="skel skel-line sm"></div>
  </div>

  <template v-else>
    <p class="section-title">Fuel Monitoring</p>
    <div class="card fuel-highlight">
      <div class="fh-main">
        <Fuel :size="26" class="fh-ic" />
        <div>
          <div class="fh-value">{{ fmt(latest?.total_litres) }} <span class="fh-unit">L</span></div>
          <div class="muted" style="font-size:13px">Current fuel level · updated {{ ago(latest?.received_at) }}</div>
        </div>
      </div>
      <div v-if="v?.tank_capacity_litres" class="fh-bar-wrap">
        <div class="fh-bar"><div class="fh-bar-fill" :style="{ width: pctFull + '%' }"></div></div>
        <div class="muted" style="font-size:12px">{{ pctFull }}% of {{ v.tank_capacity_litres }} L tank capacity</div>
      </div>
    </div>

    <p class="section-title">Fuel Refill Logs</p>
    <div class="card" style="padding:6px 0">
      <table>
        <thead><tr><th>When</th><th>Amount</th><th>Note</th></tr></thead>
        <tbody>
          <tr v-for="a in refills" :key="a.id">
            <td>{{ new Date(a.created_at).toLocaleString() }}</td>
            <td class="ico"><Plus :size="13" style="color:var(--green)" /> {{ fmt(a.meta?.delta_litres) }} L</td>
            <td class="muted">{{ a.message }}</td>
          </tr>
          <tr v-if="!refills.length"><td colspan="3" class="muted" style="padding:14px">No refill events recorded yet.</td></tr>
        </tbody>
      </table>
    </div>

    <p class="section-title">Fuel Theft Alerts</p>
    <div class="card" style="padding:6px 0">
      <table>
        <thead><tr><th>When</th><th>Amount lost</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="a in thefts" :key="a.id">
            <td>{{ new Date(a.created_at).toLocaleString() }}</td>
            <td class="ico"><Minus :size="13" style="color:var(--crit)" /> {{ fmt(Math.abs(a.meta?.delta_litres)) }} L</td>
            <td><span class="badge" :class="a.status === 'open' ? 'critical' : 'offline'">{{ a.status }}</span></td>
          </tr>
          <tr v-if="!thefts.length"><td colspan="3" class="muted" style="padding:14px">No theft alerts on file.</td></tr>
        </tbody>
      </table>
    </div>

    <p class="section-title">Fuel Consumption Reports</p>
    <div class="card" style="padding:14px 16px">
      <div class="kvs">
        <div><span class="muted">Total consumed (recent trips)</span><b>{{ fmt(totalConsumed) }} L</b></div>
        <div><span class="muted">Total distance (recent trips)</span><b>{{ fmt(totalDistance) }} km</b></div>
        <div><span class="muted">Trips with fuel data</span><b>{{ tripsWithFuel.length }}</b></div>
        <div><span class="muted">Completed trips seen</span><b>{{ completedTrips.length }}</b></div>
      </div>
    </div>

    <p class="section-title">Fuel Efficiency Analytics</p>
    <div class="card" style="padding:14px 16px">
      <template v-if="efficiencyKmpl != null">
        <div class="fh-value" style="font-size:26px">{{ fmt(efficiencyKmpl) }} <span class="fh-unit">km/L</span></div>
        <p class="muted" style="margin:6px 0 0;font-size:12.5px">Average across {{ tripsWithFuel.length }} trip(s) with recorded fuel consumption.</p>
      </template>
      <p v-else class="muted" style="margin:0">Not enough trip + fuel data yet to compute efficiency.</p>
    </div>

    <p class="section-title">Fuel Usage Trends</p>
    <div class="card" style="padding:14px 16px">
      <template v-if="trend">
        <svg class="spark" :viewBox="`0 0 ${trend.width} ${trend.height}`" preserveAspectRatio="none"
             role="img" aria-label="Fuel level trend over recent telemetry">
          <line :x1="0" :y1="trend.base" :x2="trend.width" :y2="trend.base"
                stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
          <polyline :points="trend.area" fill="var(--brand)" fill-opacity="0.10" stroke="none" />
          <polyline :points="trend.line" fill="none" stroke="var(--brand)" stroke-width="1.5"
                    stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
        </svg>
        <div class="row" style="justify-content:space-between;margin-top:6px">
          <span class="muted" style="font-size:12px">Oldest <b style="color:var(--text)">{{ fmt(litresSeries[0]) }}</b> L</span>
          <span class="muted" style="font-size:12px">Latest <b style="color:var(--text)">{{ fmt(litresSeries[litresSeries.length - 1]) }}</b> L</span>
        </div>
      </template>
      <p v-else class="muted" style="margin:0">Not enough telemetry yet to chart a trend.</p>
    </div>
  </template>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowLeft, Fuel, Plus, Minus } from 'lucide-vue-next'
import { getVehicle, getVehicleTrack, getVehicleTrips, getAlerts } from '../api'
import { fmt, ago, sparkline } from '../util'

const props = defineProps({ id: [String, Number] })
const v = ref(null)
const track = ref([])
const trips = ref([])
const refills = ref([])
const thefts = ref([])
const loading = ref(true)

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
.back-btn {
  flex: none; width: 34px; height: 34px; padding: 0; display: grid; place-items: center;
  border-radius: var(--radius-sm); color: var(--text);
}
.back-btn:hover { background: var(--surface-2); }

.fuel-highlight { padding: 18px 20px; background: var(--brand-soft); border-color: var(--brand-ring); }
.fh-main { display: flex; align-items: center; gap: 14px; }
.fh-ic { color: var(--brand); flex: none; }
.fh-value { font-size: 30px; font-weight: 800; letter-spacing: -.01em; }
.fh-unit { font-size: 16px; font-weight: 600; color: var(--muted); }

.fh-bar-wrap { margin-top: 14px; }
.fh-bar { height: 8px; border-radius: 999px; background: var(--surface); overflow: hidden; margin-bottom: 6px; }
.fh-bar-fill { height: 100%; background: var(--accent-grad); border-radius: 999px; }

.kvs { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 18px; }
.kvs div { display: flex; flex-direction: column; }
.kvs b { font-size: 16px; margin-top: 2px; }

/* Six sections back-to-back need real air between them, not just the tight
   title-to-its-own-card gap — otherwise they visually blur into one block. */
.card + .section-title { margin-top: 28px; }
</style>
