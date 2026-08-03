<template>
  <h1>My Trips</h1>
  <div class="muted" style="margin-bottom:14px">Recent journeys for your truck</div>

  <div v-if="loading">
    <div v-for="n in 5" :key="n" class="skel sk-item"></div>
  </div>
  <div v-else-if="!trips.length" class="card empty">
    <Route :size="34" :stroke-width="1.5" style="color:var(--muted)" />
    <div style="margin-top:8px">No trips recorded yet.</div>
  </div>

  <div v-else>
    <template v-for="group in grouped" :key="group.label">
      <div class="section-title">{{ group.label }}</div>
      <motion.div v-for="t in group.items" :key="t.id" class="card item"
        :class="rowClass(t)"
        :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }"
        :transition="{ duration: reduced ? 0 : 0.22, delay: reduced ? 0 : Math.min(t._idx, 8) * 0.03, ease: EASE }">
        <div class="item-row">
          <span class="item-ic" :class="iconClass(t)">
            <component :is="rowIcon(t)" :size="17" :stroke-width="2.25" />
          </span>
          <div>
            <div class="t" v-if="t.status === 'active'">
              <span class="badge on"><span class="dot"></span>Active</span>
            </div>
            <!-- completed trips are the expected/default state, so instead of
                 repeating an identical "Completed" pill on every row, this
                 shows a quiet, real title derived from the trip itself -->
            <div class="t trip-tier-label" v-else>{{ tierLabel(t) }}</div>
            <div class="d">{{ timeOnly(t.started_at) }} → {{ t.ended_at ? timeOnly(t.ended_at) : 'now' }}</div>
          </div>
        </div>
        <div style="text-align:right">
          <div class="t-numeral" :style="{ color: t.status === 'active' ? 'var(--green-strong)' : 'var(--text)' }">{{ round(t.distance_km) }} <small class="muted" style="font-size:12px;font-weight:600;letter-spacing:0">km</small></div>
          <div class="d">max {{ round(t.max_speed_kmph) }} · avg {{ round(t.avg_speed_kmph) }} km/h</div>
          <div class="dist-bar" :title="`${round(t.distance_km)} km`">
            <div class="dist-bar-fill" :class="iconClass(t)" :style="{ width: distPct(t) + '%' }"></div>
          </div>
        </div>
      </motion.div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { motion } from 'motion-v'
import { Route, Navigation, MapPin, Milestone } from 'lucide-vue-next'
import { getMyTrips } from '../api'
import { usePrefersReducedMotion, EASE } from '../motion'

const reduced = usePrefersReducedMotion()
const loading = ref(true)
const trips = ref([])

// distance tiers drive icon + accent hue per row — the single biggest lever
// for making a list of otherwise-identical "Completed" trips scannable
const TIER_ICON = { short: MapPin, medium: Route, long: Milestone }
const TIER_CLASS = { short: 'cyan', medium: 'info', long: 'violet' }
const TIER_LABEL = { short: 'Local run', medium: 'Regional run', long: 'Highway run' }
const DIST_REFERENCE_KM = 150 // bar scale reference; clamped below

function tier(km) {
  const d = km || 0
  if (d < 20) return 'short'
  if (d < 100) return 'medium'
  return 'long'
}
function rowIcon(t) { return t.status === 'active' ? Navigation : TIER_ICON[tier(t.distance_km)] }
function iconClass(t) { return t.status === 'active' ? 'on' : TIER_CLASS[tier(t.distance_km)] }
function tierLabel(t) { return TIER_LABEL[tier(t.distance_km)] }
function rowClass(t) { return t.status === 'active' ? 'trip-active' : `trip-done tier-${tier(t.distance_km)}` }
function distPct(t) { return Math.max(4, Math.min(100, Math.round(((t.distance_km || 0) / DIST_REFERENCE_KM) * 100))) }

function round(n) { return Math.round((n || 0) * 10) / 10 }
function timeOnly(s) { return s ? new Date(s).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : '—' }

// group rows by calendar day (Today / Yesterday / Weekday, Mon D) so the date
// isn't repeated on every single row and the list gets real visual rhythm
// instead of reading as one uninterrupted stack of identical widgets
function dayLabel(s) {
  const d = new Date(s)
  const startOfDay = (x) => { const c = new Date(x); c.setHours(0, 0, 0, 0); return c.getTime() }
  const today = startOfDay(new Date())
  const yesterday = today - 86400000
  const day = startOfDay(d)
  if (day === today) return 'Today'
  if (day === yesterday) return 'Yesterday'
  return d.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' })
}
const grouped = computed(() => {
  const groups = []
  let last = null
  trips.value.forEach((t, idx) => {
    const label = dayLabel(t.started_at)
    if (label !== last) { groups.push({ label, items: [] }); last = label }
    groups[groups.length - 1].items.push({ ...t, _idx: idx })
  })
  return groups
})

onMounted(async () => {
  try { trips.value = await getMyTrips() } catch (e) { /* ignore */ }
  finally { loading.value = false }
})
</script>
