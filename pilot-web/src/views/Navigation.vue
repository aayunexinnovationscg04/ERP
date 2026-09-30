<template>
  <div class="page-head">
    <div class="ph-text">
      <h1>Traffic &amp; Delays</h1>
      <div class="ph-sub">Conditions along your current route</div>
    </div>
  </div>

  <TripGate :state="tripState"
    no-truck-text="Once your fleet manager links a vehicle to your account, traffic and delay notices for your route appear here."
    no-trip-text="Traffic and delay notices appear here while your truck is on a trip.">
    <div class="notice sample-note" role="note">
      <Info :size="16" :stroke-width="2.25" />
      <span><strong>Sample traffic preview.</strong> Live traffic for your route will appear here once a traffic feed is connected.</span>
    </div>

    <div class="tr-grid">
      <motion.section class="card card-pad tr-hero" aria-label="Traffic summary"
        :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }" :transition="pageTransition(reduced)">
        <div class="tr-top">
          <div>
            <div class="stat-label">Traffic now</div>
            <div class="tr-cond">{{ summary.condition }}</div>
          </div>
          <span class="badge badge-lg warning"><Clock :size="15" :stroke-width="2.5" /> +{{ summary.delayMin }} min</span>
        </div>

        <!-- 3-step level meter: Light / Moderate / Heavy -->
        <div class="meter" role="img" :aria-label="`Traffic level: ${summary.condition}`">
          <span v-for="(lvl, i) in LEVELS" :key="lvl" class="seg" :class="{ on: i <= levelIndex, ['l' + i]: true }"></span>
        </div>
        <div class="meter-labels"><span v-for="lvl in LEVELS" :key="lvl">{{ lvl }}</span></div>

        <div class="stat-grid" style="margin-top:16px">
          <div class="stat tone-brand">
            <div class="stat-top"><span class="stat-ic"><Clock :size="17" :stroke-width="2.25" /></span><span class="stat-label">Adjusted ETA</span></div>
            <div class="stat-value">{{ summary.adjustedEta }}</div>
          </div>
          <div class="stat tone-amber">
            <div class="stat-top"><span class="stat-ic"><TrafficCone :size="17" :stroke-width="2.25" /></span><span class="stat-label">Notices</span></div>
            <div class="stat-value">{{ notices.length }}</div>
          </div>
        </div>
        <div class="dest">
          <MapPin :size="18" :stroke-width="2.25" />
          <div><div class="stat-label">Delivery location</div><div class="dest-v">{{ summary.deliveryLocation }}</div></div>
        </div>
      </motion.section>

      <section aria-label="Traffic and delay notices">
        <div class="section-title tr-list-title"><span>Notices on your route</span></div>
        <div class="stack">
          <motion.article v-for="(n, i) in notices" :key="n.id" class="card notice-card" :class="'sev-' + n.severity"
            :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: reduced ? 0 : 0.22, delay: reduced ? 0 : i * 0.04, ease: EASE }">
            <span class="row-ic" :class="TONE[n.severity]"><component :is="n.icon" :size="20" :stroke-width="2.25" /></span>
            <div class="row-main">
              <div class="row-title">{{ n.title }}</div>
              <div class="row-sub">{{ n.detail }}</div>
              <div class="row-sub loc"><MapPin :size="13" :stroke-width="2.25" /> {{ n.location }}</div>
            </div>
            <span class="badge" :class="BADGE[n.severity]">+{{ n.delayMin }} min</span>
          </motion.article>
        </div>
      </section>
    </div>
  </TripGate>
</template>

<script setup>
import { computed } from 'vue'
import { motion } from 'motion-v'
import { MapPin, Clock, TrafficCone, Construction, CircleAlert, Info } from 'lucide-vue-next'
import TripGate from '../components/TripGate.vue'
import { useTripState } from '../tripState'
import { usePrefersReducedMotion, pageTransition, EASE } from '../motion'

const reduced = usePrefersReducedMotion()
const tripState = useTripState()

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
const TONE = { critical: 'ic-red', warning: 'ic-amber', info: 'ic-info' }
const BADGE = { critical: 'critical', warning: 'warning', info: 'info' }
</script>

<style scoped>
.sample-note { margin-bottom: 14px; }
.tr-grid { display: grid; gap: 14px; grid-template-columns: minmax(0, 1fr); }
@media (min-width: 1100px) { .tr-grid { grid-template-columns: minmax(0, 5fr) minmax(0, 6fr); gap: 18px; align-items: start; } }
.tr-list-title { margin-top: 10px; }
@media (min-width: 1100px) { .tr-list-title { margin-top: 0; } }

.tr-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.tr-cond { font-size: 2.25rem; font-weight: 800; letter-spacing: -.03em; line-height: 1.1; color: var(--ink-strong); margin-top: 4px; }

.meter { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 18px; }
.seg { height: 10px; border-radius: var(--radius-pill); background: var(--surface-3); }
.seg.on.l0 { background: var(--green); }
.seg.on.l1 { background: var(--amber-strong); }
.seg.on.l2 { background: var(--red); }
.meter-labels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; margin-top: 6px; font-size: .75rem; font-weight: 700; color: var(--muted); }
.meter-labels span:nth-child(2) { text-align: center; }
.meter-labels span:nth-child(3) { text-align: right; }

.dest { display: flex; gap: 12px; align-items: flex-start; margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--border); color: var(--muted); }
.dest svg { flex: none; margin-top: 2px; }
.dest-v { color: var(--ink-strong); font-weight: 700; margin-top: 2px; }

.notice-card { display: flex; align-items: flex-start; gap: 14px; padding: 16px; border-left: 4px solid var(--border-strong); }
.notice-card.sev-critical { border-left-color: var(--crit); }
.notice-card.sev-warning { border-left-color: var(--amber); }
.notice-card.sev-info { border-left-color: var(--info); }
.loc { display: flex; align-items: center; gap: 5px; }
.loc svg { flex: none; }
</style>
