<template>
  <template v-if="loading">
    <div class="kpis"><div class="skel sk-chip" v-for="n in 3" :key="n"></div></div>
    <div class="skel sk-row" v-for="n in 6" :key="'r'+n"></div>
  </template>

  <div v-else-if="!trips.length" class="card">
    <EmptyState :icon="Route" title="No trips yet" text="Trips are recorded when your truck moves." />
  </div>

  <template v-else>
    <!-- totals for the trips listed -->
    <div class="kpis trip-kpis">
      <StatTile label="Trips" :value="trips.length" :icon="Route" tone="blue" />
      <StatTile label="Distance" :value="fmtKm(totalKm)" unit="km" :icon="Milestone" tone="brand" />
      <StatTile label="Fuel used" :value="fmtL(totalFuel)" unit="L" :icon="Fuel" tone="amber" />
    </div>

    <!-- active trip -->
    <section v-if="active" class="card active-trip" aria-label="Current trip">
      <div class="card-head">
        <div class="card-head-title"><span class="dot green"></span><h2>On trip now</h2></div>
        <span class="muted at-since">Since {{ timeOnly(active.started_at) }} · {{ duration(active.started_at) }}</span>
      </div>
      <div class="card-body at-body">
        <div class="kvs at-stats">
          <div><span class="k">So far</span><span class="v num at-v">{{ round1(active.distance_km) }} <small>km</small></span></div>
          <div><span class="k">Avg speed</span><span class="v num at-v">{{ Math.round(active.avg_speed_kmph || 0) }} <small>km/h</small></span></div>
          <div><span class="k">Top speed</span><span class="v num at-v">{{ Math.round(active.max_speed_kmph || 0) }} <small>km/h</small></span></div>
        </div>
        <div class="at-actions">
          <router-link to="/route-guidance" class="btn primary"><Navigation :size="16" /> Route guidance</router-link>
          <router-link to="/navigation" class="btn"><Compass :size="16" /> Traffic &amp; delays</router-link>
        </div>
      </div>
    </section>

    <!-- completed trips -->
    <section class="card flush" aria-label="Trip history">
      <div class="card-head">
        <div class="card-head-title"><History :size="18" /><h2>Trip history</h2></div>
        <span class="muted num" style="font-size:12.5px">{{ done.length }} trips · {{ fmtKm(doneKm) }} km</span>
      </div>
      <EmptyState v-if="!done.length" compact :icon="Route" title="No finished trips yet" />
      <template v-else>
        <div class="table-wrap">
          <table class="mstack trip-table">
            <thead>
              <tr><th>Trip</th><th>When</th><th>Duration</th><th>Speed</th><th class="num">Fuel</th><th class="num">Distance</th></tr>
            </thead>
            <tbody>
              <tr v-for="t in pager.rows.value" :key="t.id" class="trip-row">
                <td class="cell-head">
                  <div class="cell-with-icon">
                    <span class="icon-chip" :class="TIER_TONE[tier(t.distance_km)]"><component :is="TIER_ICON[tier(t.distance_km)]" :size="16" /></span>
                    <span class="cell-main">{{ TIER_LABEL[tier(t.distance_km)] }}</span>
                  </div>
                  <span class="show-sm trip-km num">{{ round1(t.distance_km) }} km</span>
                </td>
                <td data-label="When" class="nowrap"><div>{{ dayLabel(t.started_at) }}</div><div class="cell-sub">{{ timeOnly(t.started_at) }} – {{ timeOnly(t.ended_at) }}</div></td>
                <td data-label="Duration" class="nowrap">{{ duration(t.started_at, t.ended_at) }}</td>
                <td data-label="Speed" class="nowrap">avg {{ Math.round(t.avg_speed_kmph || 0) }} · max {{ Math.round(t.max_speed_kmph || 0) }} km/h</td>
                <td data-label="Fuel" class="num">{{ t.fuel_consumed_litres != null ? round1(t.fuel_consumed_litres) + ' L' : '—' }}</td>
                <td data-label="Distance" class="num cell-hide-sm"><b>{{ round1(t.distance_km) }}</b> km</td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager :pager="pager" />
      </template>
    </section>
  </template>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Route, Navigation, MapPin, Milestone, Compass, Fuel, History } from 'lucide-vue-next'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { getMyTrips } from '../api'
import { round1, timeOnly, duration, dayLabel } from '../format'

const loading = ref(true)
const trips = ref([])

// Distance tiers give otherwise-identical completed trips a scannable title + icon.
const TIER_ICON = { short: MapPin, medium: Route, long: Milestone }
const TIER_TONE = { short: 'gray', medium: 'info', long: 'info' }
const TIER_LABEL = { short: 'Local run', medium: 'Regional run', long: 'Highway run' }
function tier(km) {
  const d = km || 0
  if (d < 20) return 'short'
  if (d < 100) return 'medium'
  return 'long'
}

const active = computed(() => trips.value.find((t) => t.status === 'active') || null)
const done = computed(() => trips.value.filter((t) => t.status !== 'active'))
const totalKm = computed(() => trips.value.reduce((s, t) => s + (t.distance_km || 0), 0))
const doneKm = computed(() => done.value.reduce((s, t) => s + (t.distance_km || 0), 0))
const totalFuel = computed(() => trips.value.reduce((s, t) => s + (t.fuel_consumed_litres || 0), 0))
function fmtKm(n) { return Math.round(n).toLocaleString('en-IN') }
function fmtL(n) { return (Math.round(n * 10) / 10).toLocaleString('en-IN') }

const pager = usePaging(done, 10)

onMounted(async () => {
  try { trips.value = await getMyTrips() } catch (e) { /* show empty state */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.active-trip { margin-bottom: 16px; border-top: 3px solid var(--green); }
.at-since { font-size: 12.5px; font-weight: 600; }
.at-body { display: flex; align-items: center; gap: 14px 24px; flex-wrap: wrap; }
.at-stats { flex: 1 1 320px; grid-template-columns: repeat(3, minmax(0, 1fr)); }
.at-v small { font-size: 12px; font-weight: 700; color: var(--muted); }
.at-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.trip-km { font-weight: 800; color: var(--ink-strong); white-space: nowrap; }
@media (max-width: 720px) {
  .at-actions { width: 100%; }
  .at-actions .btn { flex: 1 1 160px; }
}
</style>
