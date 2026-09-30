<template>
  <PageHeader :preview="showTrip" />

  <TripGate :state="tripState" no-trip-text="Shown while your truck is on a trip.">
    <div class="kpis">
      <StatTile label="Traffic now" :value="summary.condition" :icon="TrafficCone" tone="amber" />
      <StatTile label="Delay" :value="'+' + summary.delayMin" unit="min" :icon="Clock" tone="red" />
      <StatTile label="ETA" :value="summary.adjustedEta" :icon="Flag" tone="brand" />
      <StatTile label="Notices" :value="notices.length" :icon="CircleAlert" tone="blue" />
    </div>

    <div class="grid-2">
      <section class="card flush" aria-label="Traffic and delay notices">
        <div class="card-head">
          <div class="card-head-title"><CircleAlert :size="18" /><h2>Notices</h2></div>
        </div>
        <div class="list">
          <article v-for="(n, i) in notices" :key="n.id" class="list-row notice-row item-in" :style="{ animationDelay: Math.min(i, 8) * 40 + 'ms' }">
            <span class="icon-chip" :class="TONE[n.severity]"><component :is="n.icon" :size="16" /></span>
            <div class="grow">
              <div class="title">{{ n.title }}</div>
              <div class="sub">{{ n.detail }}</div>
              <div class="sub loc"><MapPin :size="12" /> {{ n.location }}</div>
            </div>
            <span class="badge nt" :class="BADGE[n.severity]">+{{ n.delayMin }} min</span>
          </article>
        </div>
      </section>

      <section class="card" aria-label="Traffic level">
        <div class="card-head">
          <div class="card-head-title"><Gauge :size="18" /><h2>Traffic level</h2></div>
          <span class="badge warning">{{ summary.condition }}</span>
        </div>
        <div class="card-body">
          <!-- 3-step level meter: Light / Moderate / Heavy -->
          <div class="lvl" role="img" :aria-label="`Traffic level: ${summary.condition}`">
            <span v-for="(lvl, i) in LEVELS" :key="lvl" class="lvl-seg" :class="{ on: i <= levelIndex, ['l' + i]: true }"></span>
          </div>
          <div class="lvl-labels"><span v-for="lvl in LEVELS" :key="lvl">{{ lvl }}</span></div>
          <div class="kvs" style="margin-top:16px">
            <div style="grid-column:1/-1"><span class="k">Delivery</span><span class="v">{{ summary.deliveryLocation }}</span></div>
          </div>
        </div>
      </section>
    </div>
  </TripGate>
</template>

<script setup>
import { computed } from 'vue'
import { MapPin, Clock, TrafficCone, Construction, CircleAlert, Flag, Gauge } from 'lucide-vue-next'
import TripGate from '../components/TripGate.vue'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import { useTripState } from '../tripState'

const tripState = useTripState()
const showTrip = computed(() => !tripState.loading.value && !tripState.failed.value && tripState.assigned.value && tripState.onTrip.value)

// Sample data — shaped like a future live traffic feed (a condition summary
// plus located notices) so it can be pointed at a real source later.
const summary = {
  condition: 'Moderate',
  delayMin: 12,
  deliveryLocation: 'Sector 12 Industrial Area, Raipur, CG',
  adjustedEta: '2:57 PM',
}
const LEVELS = ['Light', 'Moderate', 'Heavy']
const levelIndex = computed(() => Math.max(0, LEVELS.indexOf(summary.condition)))

const notices = [
  { id: 3, severity: 'critical', icon: CircleAlert, title: 'Accident reported', detail: 'Partial road blockage, expect diversion', location: 'Sector 12 Main Road', delayMin: 15 },
  { id: 1, severity: 'warning', icon: TrafficCone, title: 'Heavy congestion ahead', detail: 'Slow-moving traffic near Ring Road junction', location: 'Ring Road, 6 km ahead', delayMin: 8 },
  { id: 2, severity: 'info', icon: Construction, title: 'Road work', detail: 'One lane closed for resurfacing', location: 'NH-30 near Tilda', delayMin: 3 },
]
const TONE = { critical: 'crit', warning: 'amber', info: 'info' }
const BADGE = { critical: 'critical', warning: 'warning', info: 'info' }
</script>

<style scoped>
.notice-row { align-items: flex-start; }
.notice-row .sub { white-space: normal; }
.loc { display: flex; align-items: center; gap: 5px; margin-top: 2px; }
.loc svg { flex: none; }
.lvl { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
.lvl-seg { height: 10px; border-radius: var(--radius-pill); background: var(--surface-3); }
.lvl-seg.on.l0 { background: var(--green); }
.lvl-seg.on.l1 { background: var(--amber); }
.lvl-seg.on.l2 { background: var(--red); }
.lvl-labels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 6px; font-size: 12px; font-weight: 600; color: var(--muted); }
.lvl-labels span:nth-child(2) { text-align: center; }
.lvl-labels span:nth-child(3) { text-align: right; }
</style>
