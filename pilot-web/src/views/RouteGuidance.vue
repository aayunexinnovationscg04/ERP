<template>
  <div class="page-head">
    <div class="ph-text">
      <h1>Route Guidance</h1>
      <div class="ph-sub">Turn-by-turn for your current trip</div>
    </div>
  </div>

  <TripGate :state="tripState"
    no-truck-text="Once your fleet manager links a vehicle to your account, turn-by-turn directions for your trips appear here."
    no-trip-text="Directions appear here while your truck is on a trip.">
    <div class="notice sample-note" role="note">
      <Info :size="16" :stroke-width="2.25" />
      <span><strong>Sample route preview.</strong> Live turn-by-turn directions will appear here once dispatch assigns a route to your trip.</span>
    </div>

    <div class="rg-grid">
      <!-- next manoeuvre -->
      <motion.section class="next-turn" aria-label="Next direction"
        :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }" :transition="pageTransition(reduced)">
        <span class="nt-ic"><component :is="directions[0].icon" :size="40" :stroke-width="2.5" /></span>
        <div class="nt-body">
          <div class="nt-dist num">{{ directions[0].distance }}</div>
          <div class="nt-instr">{{ directions[0].instruction }}</div>
          <div class="nt-road">{{ directions[0].road }}</div>
        </div>
      </motion.section>

      <!-- trip figures -->
      <section class="card card-pad rg-stats" aria-label="Trip progress">
        <div class="stat-grid">
          <div class="stat tone-brand">
            <div class="stat-top"><span class="stat-ic"><Clock :size="17" :stroke-width="2.25" /></span><span class="stat-label">ETA</span></div>
            <div class="stat-value">{{ trip.eta }}</div>
          </div>
          <div class="stat tone-info">
            <div class="stat-top"><span class="stat-ic"><Milestone :size="17" :stroke-width="2.25" /></span><span class="stat-label">Remaining</span></div>
            <div class="stat-value">{{ trip.distanceLeft }}<small>km</small></div>
          </div>
        </div>
        <ul class="list dest-list">
          <li class="list-row">
            <span class="row-ic ic-neutral"><Timer :size="19" :stroke-width="2.25" /></span>
            <div class="row-main"><div class="row-sub">Time left</div><div class="row-title">{{ trip.timeLeft }}</div></div>
          </li>
          <li class="list-row">
            <span class="row-ic ic-neutral"><Flag :size="19" :stroke-width="2.25" /></span>
            <div class="row-main"><div class="row-sub">Next stop</div><div class="row-title">{{ trip.nextStop }}</div></div>
          </li>
          <li class="list-row">
            <span class="row-ic ic-neutral"><MapPin :size="19" :stroke-width="2.25" /></span>
            <div class="row-main"><div class="row-sub">Delivery location</div><div class="row-title">{{ trip.deliveryLocation }}</div></div>
          </li>
        </ul>
      </section>

      <!-- all steps -->
      <section class="card steps-card" aria-label="Upcoming directions">
        <div class="card-head">
          <span class="ch-ic ic-info"><Navigation :size="18" :stroke-width="2.25" /></span>
          <div class="ch-text"><h2>Upcoming directions</h2><div class="ch-sub">{{ directions.length }} steps to destination</div></div>
        </div>
        <ol class="steps">
          <motion.li v-for="(step, i) in directions" :key="i" class="step" :class="{ current: i === 0, last: i === directions.length - 1 }"
            :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: reduced ? 0 : 0.22, delay: reduced ? 0 : i * 0.04, ease: EASE }">
            <span class="step-ic"><component :is="step.icon" :size="18" :stroke-width="2.5" /></span>
            <div class="row-main">
              <div class="row-title">{{ step.instruction }}</div>
              <div class="row-sub">{{ step.road }}</div>
            </div>
            <div class="step-dist num">{{ step.distance }}</div>
          </motion.li>
        </ol>
      </section>
    </div>
  </TripGate>
</template>

<script setup>
import { motion } from 'motion-v'
import { Flag, Milestone, Clock, MapPin, CornerUpRight, CornerUpLeft, ArrowUp, Info, Navigation, Timer } from 'lucide-vue-next'
import TripGate from '../components/TripGate.vue'
import { useTripState } from '../tripState'
import { usePrefersReducedMotion, pageTransition, EASE } from '../motion'

const reduced = usePrefersReducedMotion()
const tripState = useTripState()

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
.sample-note { margin-bottom: 14px; }
.rg-grid { display: grid; gap: 14px; grid-template-columns: minmax(0, 1fr); }
@media (min-width: 1100px) {
  .rg-grid { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 18px; align-items: start; }
  .next-turn { grid-column: 1 / -1; }
}

/* the one dark block on the page: reads like a nav-app manoeuvre banner */
.next-turn {
  display: flex; align-items: center; gap: 18px; padding: 20px;
  border-radius: var(--radius); background: var(--navy-800); color: #FFFFFF;
  border: 1px solid var(--navy-700);
}
:root[data-theme="dark"] .next-turn { background: var(--navy-700); border-color: var(--navy-600); }
.nt-ic { flex: none; width: 72px; height: 72px; border-radius: var(--radius); display: grid; place-items: center; background: var(--brand); color: #FFFFFF; }
.nt-body { min-width: 0; }
.nt-dist { font-size: 2.25rem; font-weight: 800; letter-spacing: -.03em; line-height: 1; }
.nt-instr { font-size: 1.125rem; font-weight: 700; margin-top: 6px; line-height: 1.3; }
.nt-road { font-size: .875rem; color: var(--ink-muted); margin-top: 2px; }

.rg-stats { display: flex; flex-direction: column; gap: 6px; }
.dest-list .list-row { padding: 12px 2px; min-height: 0; }
.dest-list .row-sub { margin: 0 0 2px; font-size: .75rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }

.steps { list-style: none; margin: 0; padding: 6px 0; }
.step { position: relative; display: flex; align-items: center; gap: 14px; padding: 12px 16px; min-height: 64px; }
/* connector line between step markers */
.step:not(.last)::after {
  content: ""; position: absolute; left: 35px; top: 50px; bottom: -14px; width: 2px; background: var(--border);
}
.step-ic {
  position: relative; z-index: 1; flex: none; width: 40px; height: 40px; border-radius: 50%;
  display: grid; place-items: center; background: var(--surface-3); color: var(--muted); border: 2px solid var(--surface);
}
.step.current .step-ic { background: var(--brand); color: #FFFFFF; }
.step-dist { flex: none; font-weight: 800; font-size: 1rem; color: var(--ink-strong); white-space: nowrap; }

@media (max-width: 400px) {
  .next-turn { padding: 16px; gap: 14px; }
  .nt-ic { width: 60px; height: 60px; }
  .nt-dist { font-size: 1.875rem; }
  .nt-instr { font-size: 1rem; }
}
</style>
