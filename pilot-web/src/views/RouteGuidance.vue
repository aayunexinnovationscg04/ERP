<template>
  <PageHeader :preview="showTrip" />

  <TripGate :state="tripState" no-trip-text="Shown while your truck is on a trip.">
    <div class="kpis">
      <StatTile label="ETA" :value="trip.eta" :icon="Clock" tone="brand" />
      <StatTile label="To go" :value="trip.distanceLeft" unit="km" :icon="Milestone" tone="blue" />
      <StatTile label="Time left" :value="trip.timeLeft" :icon="Timer" tone="teal" />
    </div>

    <!-- next manoeuvre -->
    <section class="card next-turn" aria-label="Next direction">
      <span class="nt-ic"><component :is="directions[0].icon" :size="30" /></span>
      <div class="nt-body">
        <div class="nt-dist num">{{ directions[0].distance }}</div>
        <div class="nt-instr">{{ directions[0].instruction }}</div>
        <div class="nt-road">{{ directions[0].road }}</div>
      </div>
    </section>

    <div class="grid-2">
      <!-- all steps -->
      <section class="card flush steps-card" aria-label="Upcoming directions">
        <div class="card-head">
          <div class="card-head-title"><Navigation :size="18" /><h2>Directions</h2></div>
        </div>
        <ol class="steps">
          <li v-for="(step, i) in directions" :key="i" class="step item-in" :class="{ current: i === 0, last: i === directions.length - 1 }"
            :style="{ animationDelay: Math.min(i, 8) * 40 + 'ms' }">
            <span class="step-ic"><component :is="step.icon" :size="16" /></span>
            <div class="grow">
              <div class="title">{{ step.instruction }}</div>
              <div class="sub">{{ step.road }}</div>
            </div>
            <div class="step-dist num">{{ step.distance }}</div>
          </li>
        </ol>
      </section>

      <!-- destination -->
      <section class="card" aria-label="Destination">
        <div class="card-head">
          <div class="card-head-title"><Flag :size="18" /><h2>Destination</h2></div>
        </div>
        <div class="card-body">
          <div class="kvs">
            <div style="grid-column:1/-1"><span class="k">Next stop</span><span class="v">{{ trip.nextStop }}</span></div>
            <div style="grid-column:1/-1"><span class="k">Delivery</span><span class="v">{{ trip.deliveryLocation }}</span></div>
          </div>
        </div>
      </section>
    </div>
  </TripGate>
</template>

<script setup>
import { computed } from 'vue'
import { Flag, Milestone, Clock, CornerUpRight, CornerUpLeft, ArrowUp, Navigation, Timer } from 'lucide-vue-next'
import TripGate from '../components/TripGate.vue'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import { useTripState } from '../tripState'

const tripState = useTripState()
const showTrip = computed(() => !tripState.loading.value && !tripState.failed.value && tripState.assigned.value && tripState.onTrip.value)

// Sample data — no live routing engine is wired up yet. Shaped like a real
// directions API response so the page can switch to live data later.
const trip = {
  eta: '2:45 PM',
  nextStop: 'Raipur Fuel Depot',
  distanceLeft: 42,
  timeLeft: '58 min',
  deliveryLocation: 'Sector 12 Industrial Area, Raipur, CG',
}

const directions = [
  { icon: ArrowUp, instruction: 'Continue straight on NH-30', road: 'NH-30, towards Raipur', distance: '18 km' },
  { icon: CornerUpRight, instruction: 'Turn right onto Ring Road', road: 'Raipur Ring Road', distance: '26 km' },
  { icon: CornerUpLeft, instruction: 'Turn left onto Sector 12 Main Rd', road: 'Sector 12 Main Road', distance: '40 km' },
  { icon: Flag, instruction: 'Arrive at delivery location', road: 'Sector 12 Industrial Area', distance: '42 km' },
]
</script>

<style scoped>
/* next manoeuvre: the one navy block on the page, like a nav-app banner */
.next-turn {
  display: flex; align-items: center; gap: 16px; padding: 16px 18px; margin-bottom: 16px;
  background: var(--navy-900); border-color: var(--navy-900); color: #FFFFFF;
}
:root[data-theme="dark"] .next-turn { background: var(--navy-800); border-color: var(--navy-700); }
.nt-ic { flex: none; width: 56px; height: 56px; border-radius: 12px; display: grid; place-items: center; background: var(--brand); color: #FFFFFF; }
.nt-body { min-width: 0; }
.nt-dist { font-size: 1.75rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; }
.nt-instr { font-size: 15px; font-weight: 700; margin-top: 4px; line-height: 1.3; }
.nt-road { font-size: 13px; color: #C9D4E1; margin-top: 1px; }

.steps { list-style: none; margin: 0; padding: 6px 0; }
.step { position: relative; display: flex; align-items: center; gap: 12px; padding: 10px 16px; min-height: 58px; }
.step .grow { flex: 1; min-width: 0; }
.step .title { font-weight: 700; color: var(--ink-strong); }
.step .sub { font-size: 12.5px; color: var(--muted); }
/* connector line between step markers */
.step:not(.last)::after { content: ""; position: absolute; left: 31px; top: 42px; bottom: -12px; width: 2px; background: var(--border); }
.step-ic {
  position: relative; z-index: 1; flex: none; width: 32px; height: 32px; border-radius: 50%;
  display: grid; place-items: center; background: var(--surface-3); color: var(--muted); border: 2px solid var(--surface);
}
.step.current .step-ic { background: var(--brand); color: #FFFFFF; }
.step-dist { flex: none; font-weight: 800; color: var(--ink-strong); white-space: nowrap; }
@media (max-width: 400px) {
  .next-turn { padding: 14px; gap: 12px; }
  .nt-ic { width: 48px; height: 48px; }
  .nt-dist { font-size: 1.5rem; }
}
</style>
