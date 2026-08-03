<template>
  <h1>Traffic &amp; Delays</h1>
  <div class="muted" style="margin-bottom:14px">Conditions along your current route</div>

  <motion.div class="card hero"
    :initial="{ opacity: 0, y: reduced ? 0 : 10 }" :animate="{ opacity: 1, y: 0 }"
    :transition="pageTransition(reduced)">
    <div class="row">
      <div>
        <div class="reg" style="font-size:24px">{{ summary.condition }}</div>
        <div class="sub">Current traffic condition</div>
      </div>
      <div class="spacer"></div>
      <span class="badge warning"><span class="dot"></span>{{ summary.delayMin }} min delay</span>
    </div>
    <div class="chips">
      <div class="chip">
        <span class="chip-ic cyan"><MapPin :size="17" :stroke-width="2.25" /></span>
        <div class="chip-body"><div class="l">Delivery location</div><div class="v" style="font-size:13.5px; line-height:1.3">{{ summary.deliveryLocation }}</div></div>
      </div>
      <div class="chip">
        <span class="chip-ic amber"><Clock :size="17" :stroke-width="2.25" /></span>
        <div class="chip-body"><div class="l">Adjusted ETA</div><div class="v" style="font-size:16px">{{ summary.adjustedEta }}</div></div>
      </div>
    </div>
  </motion.div>

  <div class="section-title">Traffic &amp; delay notices</div>
  <motion.div v-for="(n, i) in notices" :key="n.id" class="card item"
    :class="'sev-' + n.severity"
    :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }"
    :transition="{ duration: reduced ? 0 : 0.22, delay: reduced ? 0 : Math.min(i, 8) * 0.03, ease: EASE }">
    <div class="item-row">
      <span class="item-ic" :class="n.severity === 'critical' ? 'critical' : n.severity === 'warning' ? 'warning' : 'info'">
        <component :is="n.icon" :size="17" :stroke-width="2.25" />
      </span>
      <div>
        <div class="t">{{ n.title }}</div>
        <div class="d">{{ n.detail }}</div>
        <div class="d">{{ n.location }}</div>
      </div>
    </div>
    <div style="text-align:right; align-self:flex-start">
      <span class="badge" :class="n.severity === 'critical' ? 'critical' : n.severity === 'warning' ? 'warning' : 'info'">
        <span class="dot"></span>+{{ n.delayMin }} min
      </span>
    </div>
  </motion.div>
</template>

<script setup>
import { motion } from 'motion-v'
import { MapPin, Clock, TrafficCone, Construction, CircleAlert } from 'lucide-vue-next'
import { usePrefersReducedMotion, pageTransition, EASE } from '../motion'

const reduced = usePrefersReducedMotion()

// Mock data — mirrors a future live traffic feed's shape (condition summary +
// a list of dated/located notices) so this can be pointed at a real source later.
const summary = {
  condition: 'Moderate',
  delayMin: 12,
  deliveryLocation: 'Sector 12 Industrial Area, Raipur, CG',
  adjustedEta: '2:57 PM',
}

const notices = [
  { id: 1, severity: 'warning', icon: TrafficCone, title: 'Heavy congestion ahead', detail: 'Slow-moving traffic near Ring Road junction', location: 'Ring Road, 6 km ahead', delayMin: 8 },
  { id: 2, severity: 'info', icon: Construction, title: 'Road work', detail: 'One lane closed for resurfacing', location: 'NH-30 near Tilda', delayMin: 3 },
  { id: 3, severity: 'critical', icon: CircleAlert, title: 'Accident reported', detail: 'Partial road blockage, expect diversion', location: 'Sector 12 Main Road', delayMin: 15 },
]
</script>
