<template>
  <div class="page-head">
    <div class="ph-text">
      <h1>Trips</h1>
    </div>
  </div>

  <div v-if="loading">
    <div class="skel" style="height:84px; margin-bottom:14px"></div>
    <div v-for="n in 5" :key="n" class="skel sk-item"></div>
  </div>

  <div v-else-if="!trips.length" class="card empty-state">
    <span class="empty-ic"><Route :size="34" :stroke-width="1.75" /></span>
    <h2>No trips yet</h2>
    <p>Trips are recorded when your truck moves.</p>
  </div>

  <template v-else>
    <!-- totals for the trips listed -->
    <section class="card totals" aria-label="Trip totals">
      <div class="tot"><span class="tot-v num">{{ trips.length }}</span><span class="tot-l">Trips</span></div>
      <div class="tot"><span class="tot-v num">{{ fmtKm(totalKm) }}<small>km</small></span><span class="tot-l">Distance</span></div>
      <div class="tot"><span class="tot-v num">{{ fmtL(totalFuel) }}<small>L</small></span><span class="tot-l">Fuel used</span></div>
    </section>

    <!-- active trip -->
    <motion.section v-if="active" class="card active-trip" aria-label="Current trip"
      :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }" :transition="pageTransition(reduced)">
      <div class="at-head">
        <span class="badge badge-lg on"><span class="dot"></span>On trip now</span>
        <span class="muted at-since">Since {{ timeOnly(active.started_at) }} · {{ duration(active.started_at) }}</span>
      </div>
      <div class="at-stats">
        <div><span class="at-v num">{{ round1(active.distance_km) }}<small>km</small></span><span class="at-l">So far</span></div>
        <div><span class="at-v num">{{ Math.round(active.avg_speed_kmph || 0) }}<small>km/h</small></span><span class="at-l">Avg speed</span></div>
        <div><span class="at-v num">{{ Math.round(active.max_speed_kmph || 0) }}<small>km/h</small></span><span class="at-l">Top speed</span></div>
      </div>
      <div class="at-actions">
        <router-link to="/route-guidance" class="btn btn-primary"><Navigation :size="18" :stroke-width="2.25" /> Route guidance</router-link>
        <router-link to="/navigation" class="btn"><Compass :size="18" :stroke-width="2.25" /> Traffic &amp; delays</router-link>
      </div>
    </motion.section>

    <!-- completed trips, grouped by day -->
    <div class="day-grid">
    <div v-for="group in grouped" :key="group.label" class="day-group">
      <div class="section-title">
        <span>{{ group.label }}</span><span class="spacer"></span>
        <span v-if="group.items.length > 1" class="st-meta num">{{ group.items.length }} trips · {{ fmtKm(group.km) }} km</span>
      </div>
      <ul class="card list item-in" :style="{ animationDelay: Math.min(group.idx, 6) * 40 + 'ms' }">
        <li v-for="t in group.items" :key="t.id" class="list-row">
          <span class="row-ic" :class="TIER_TONE[tier(t.distance_km)]">
            <component :is="TIER_ICON[tier(t.distance_km)]" :size="20" :stroke-width="2.25" />
          </span>
          <div class="row-main">
            <div class="row-title">{{ TIER_LABEL[tier(t.distance_km)] }}</div>
            <div class="row-sub">
              <span class="nowrap">{{ timeOnly(t.started_at) }} – {{ timeOnly(t.ended_at) }}</span>
              <span class="sep">·</span><span class="nowrap">{{ duration(t.started_at, t.ended_at) }}</span>
            </div>
            <div class="row-sub">
              <span class="nowrap">avg {{ Math.round(t.avg_speed_kmph || 0) }} · max {{ Math.round(t.max_speed_kmph || 0) }} km/h</span>
              <template v-if="t.fuel_consumed_litres != null"><span class="sep">·</span><span class="nowrap">{{ round1(t.fuel_consumed_litres) }} L</span></template>
            </div>
          </div>
          <div class="row-end">
            <div class="row-num">{{ round1(t.distance_km) }}<small>km</small></div>
          </div>
        </li>
      </ul>
    </div>
    </div>
  </template>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { motion } from 'motion-v'
import { Route, Navigation, MapPin, Milestone, Compass } from 'lucide-vue-next'
import { getMyTrips } from '../api'
import { round1, timeOnly, duration, dayLabel } from '../format'
import { usePrefersReducedMotion, pageTransition, EASE } from '../motion'

const reduced = usePrefersReducedMotion()
const loading = ref(true)
const trips = ref([])

// Distance tiers give otherwise-identical completed trips a scannable title + icon.
const TIER_ICON = { short: MapPin, medium: Route, long: Milestone }
const TIER_TONE = { short: 'ic-neutral', medium: 'ic-info', long: 'ic-info' }
const TIER_LABEL = { short: 'Local run', medium: 'Regional run', long: 'Highway run' }
function tier(km) {
  const d = km || 0
  if (d < 20) return 'short'
  if (d < 100) return 'medium'
  return 'long'
}

const active = computed(() => trips.value.find((t) => t.status === 'active') || null)
const totalKm = computed(() => trips.value.reduce((s, t) => s + (t.distance_km || 0), 0))
const totalFuel = computed(() => trips.value.reduce((s, t) => s + (t.fuel_consumed_litres || 0), 0))
function fmtKm(n) { return Math.round(n).toLocaleString('en-IN') }
function fmtL(n) { return (Math.round(n * 10) / 10).toLocaleString('en-IN') }

// completed trips grouped by calendar day (Today / Yesterday / Fri, 25 Sep)
const grouped = computed(() => {
  const groups = []
  let last = null
  trips.value.filter((t) => t.status !== 'active').forEach((t) => {
    const label = dayLabel(t.started_at)
    if (label !== last) { groups.push({ label, items: [], km: 0, idx: groups.length }); last = label }
    const g = groups[groups.length - 1]
    g.items.push(t)
    g.km += t.distance_km || 0
  })
  return groups
})

onMounted(async () => {
  try { trips.value = await getMyTrips() } catch (e) { /* show empty state */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.totals { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin-bottom: 14px; }
.tot { display: flex; flex-direction: column; gap: 2px; padding: 14px 16px; min-width: 0; }
.tot + .tot { border-left: 1px solid var(--border); }
.tot-v { font-size: 1.5rem; font-weight: 800; letter-spacing: -.02em; color: var(--ink-strong); line-height: 1.15; white-space: nowrap; }
.tot-v small { font-size: .75rem; font-weight: 650; color: var(--muted); margin-left: 2px; letter-spacing: 0; }
.tot-l { font-size: .75rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; color: var(--muted); }

.active-trip { padding: 18px; border-top: 4px solid var(--green); display: flex; flex-direction: column; gap: 16px; }
.at-head { display: flex; align-items: center; gap: 10px 12px; flex-wrap: wrap; }
.at-since { font-size: .875rem; font-weight: 600; }
.at-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; }
.at-stats > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.at-v { font-size: 1.75rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; color: var(--ink-strong); white-space: nowrap; }
.at-v small { font-size: .75rem; font-weight: 650; color: var(--muted); margin-left: 3px; letter-spacing: 0; }
.at-l { font-size: .75rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; color: var(--muted); }
.at-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.at-actions .btn { min-width: 0; }

.day-grid { display: grid; grid-template-columns: minmax(0, 1fr); column-gap: 18px; row-gap: 20px; margin-top: 22px; }
.day-group .section-title { margin-top: 0; }
@media (min-width: 1100px) { .day-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.row-sub .sep { margin: 0 6px; color: var(--muted-2); }
.nowrap { white-space: nowrap; }

@media (max-width: 400px) {
  .tot { padding: 12px; }
  .tot-v { font-size: 1.25rem; }
  .at-v { font-size: 1.375rem; }
}
@media (max-width: 479.98px) { .at-actions { grid-template-columns: 1fr; } }
@media (min-width: 768px) {
  .at-actions { display: flex; }
}
</style>
