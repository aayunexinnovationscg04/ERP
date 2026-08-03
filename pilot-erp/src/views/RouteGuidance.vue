<template>
  <h1>Route Guidance</h1>
  <div class="muted" style="margin-bottom:14px">Turn-by-turn for your current trip</div>

  <motion.div class="card hero"
    :initial="{ opacity: 0, y: reduced ? 0 : 10 }" :animate="{ opacity: 1, y: 0 }"
    :transition="pageTransition(reduced)">
    <div class="row">
      <div>
        <div class="reg">{{ trip.eta }}</div>
        <div class="sub">Estimated arrival</div>
      </div>
      <div class="spacer"></div>
      <span class="badge on"><span class="dot"></span>En route</span>
    </div>

    <div class="chips">
      <div class="chip">
        <span class="chip-ic blue"><Flag :size="17" :stroke-width="2.25" /></span>
        <div class="chip-body"><div class="l">Next stop</div><div class="v" style="font-size:16px">{{ trip.nextStop }}</div></div>
      </div>
      <div class="chip">
        <span class="chip-ic violet"><Milestone :size="17" :stroke-width="2.25" /></span>
        <div class="chip-body"><div class="l">Distance left</div><div class="v">{{ trip.distanceLeft }} <small class="muted">km</small></div></div>
      </div>
      <div class="chip">
        <span class="chip-ic emerald"><Clock :size="17" :stroke-width="2.25" /></span>
        <div class="chip-body"><div class="l">Time left</div><div class="v">{{ trip.timeLeft }}</div></div>
      </div>
      <div class="chip">
        <span class="chip-ic cyan"><MapPin :size="17" :stroke-width="2.25" /></span>
        <div class="chip-body"><div class="l">Delivery location</div><div class="v" style="font-size:13.5px; line-height:1.3">{{ trip.deliveryLocation }}</div></div>
      </div>
    </div>
  </motion.div>

  <div class="section-title">Upcoming directions</div>
  <motion.div v-for="(step, i) in directions" :key="i" class="card item"
    :class="i === 0 ? 'trip-active' : ''"
    :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }"
    :transition="{ duration: reduced ? 0 : 0.22, delay: reduced ? 0 : Math.min(i, 8) * 0.03, ease: EASE }">
    <div class="item-row">
      <span class="item-ic" :class="i === 0 ? 'on' : 'info'">
        <component :is="step.icon" :size="17" :stroke-width="2.25" />
      </span>
      <div>
        <div class="t">{{ step.instruction }}</div>
        <div class="d">{{ step.road }}</div>
      </div>
    </div>
    <div style="text-align:right">
      <div class="t-numeral" style="font-size:18px">{{ step.distance }}</div>
      <div class="d">{{ i === 0 ? 'next' : '' }}</div>
    </div>
  </motion.div>

  <div class="muted" style="font-size:12px; margin-top:12px; text-align:center">
    Mock guidance preview — live turn-by-turn syncs once dispatch assigns a route.
  </div>
</template>

<script setup>
import { motion } from 'motion-v'
import { Flag, Milestone, Clock, MapPin, CornerUpRight, CornerUpLeft, ArrowUp } from 'lucide-vue-next'
import { usePrefersReducedMotion, pageTransition, EASE } from '../motion'

const reduced = usePrefersReducedMotion()

// Mock data — no live routing engine wired up yet; mirrors the shape a real
// directions API would return so this page can be swapped to live data later.
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
