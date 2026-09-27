<template>
  <div class="page-head">
    <div class="ph-text">
      <h1>Alerts</h1>
      <div class="ph-sub">
        <template v-if="!loading && alerts.length">{{ openCount }} open · {{ alerts.length }} total</template>
        <template v-else>Safety &amp; security notices for your truck</template>
      </div>
    </div>
  </div>

  <div v-if="!loading && alerts.length" class="filter-chips" role="toolbar" aria-label="Filter alerts">
    <button v-for="c in CATEGORIES" :key="c.key" type="button" class="filter-chip" :class="{ active: activeCat === c.key }"
      :aria-pressed="activeCat === c.key" @click="activeCat = c.key">
      {{ c.label }}<span class="filter-chip-count">{{ countFor(c) }}</span>
    </button>
  </div>

  <div v-if="loading">
    <div v-for="n in 4" :key="n" class="skel" style="height:118px; margin-bottom:12px"></div>
  </div>

  <div v-else-if="!alerts.length" class="card empty-state">
    <span class="empty-ic ok"><ShieldCheck :size="34" :stroke-width="1.75" /></span>
    <h2>All clear</h2>
    <p>No alerts for your truck. Overspeed, fuel and security warnings will appear here the moment they're raised.</p>
  </div>

  <div v-else-if="!filtered.length" class="card empty-state">
    <span class="empty-ic"><CircleCheck :size="34" :stroke-width="1.75" /></span>
    <h2>No {{ activeCatLabel }} alerts</h2>
    <p>Nothing in this category right now.</p>
    <div class="empty-actions"><button type="button" class="btn" @click="activeCat = 'all'">Show all alerts</button></div>
  </div>

  <div v-else class="alert-list">
    <motion.article v-for="(a, i) in filtered" :key="a.id" class="card alert-card" :class="'sev-' + sev(a.severity)"
      :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }"
      :transition="{ duration: reduced ? 0 : 0.22, delay: reduced ? 0 : Math.min(i, 8) * 0.03, ease: EASE }">
      <div class="ac-top">
        <span class="row-ic" :class="SEV_TONE[sev(a.severity)]">
          <component :is="SEV_ICON[sev(a.severity)]" :size="20" :stroke-width="2.25" />
        </span>
        <div class="ac-main">
          <div class="ac-title">{{ a.title || a.type_label || a.type }}</div>
          <div class="ac-meta">
            <template v-if="a.title && a.type_label && a.title !== a.type_label"><span>{{ a.type_label }}</span><span class="sep">·</span></template>
            <time :datetime="a.created_at" :title="dateTime(a.created_at)">{{ timeAgo(a.created_at) }}</time>
          </div>
        </div>
        <span class="badge" :class="SEV_BADGE[sev(a.severity)]">{{ SEV_LABEL[sev(a.severity)] }}</span>
      </div>
      <p v-if="a.message" class="ac-msg">{{ a.message }}</p>
      <div class="ac-foot">
        <span class="badge" :class="STATUS_BADGE[a.status] || 'neutral'"><span class="dot"></span>{{ STATUS_LABEL[a.status] || a.status }}</span>
        <span class="muted ac-when">{{ dateTime(a.created_at) }}</span>
        <span class="spacer"></span>
        <a v-if="a.lat != null && a.lng != null" class="btn btn-sm btn-ghost ac-map"
          :href="`https://www.google.com/maps/search/?api=1&query=${a.lat},${a.lng}`" target="_blank" rel="noopener">
          <MapPin :size="16" :stroke-width="2.25" /> Location
        </a>
      </div>
    </motion.article>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { motion } from 'motion-v'
import { CircleCheck, TriangleAlert, ShieldAlert, Info, ShieldCheck, MapPin } from 'lucide-vue-next'
import { getMyAlerts } from '../api'
import { timeAgo, dateTime } from '../format'
import { usePrefersReducedMotion, EASE } from '../motion'

const reduced = usePrefersReducedMotion()
const loading = ref(true)
const alerts = ref([])

// Category chips come from the alert `type`/`severity` the endpoint returns.
// "Emergency" has no dedicated backend type, so it maps to critical severity.
const CATEGORIES = [
  { key: 'all', label: 'All' },
  { key: 'overspeed', label: 'Overspeed', types: ['overspeed'] },
  { key: 'route', label: 'Route', types: ['geofence_breach', 'idle_too_long'] },
  { key: 'fuel', label: 'Fuel', types: ['low_fuel', 'fuel_fill', 'fuel_theft'] },
  { key: 'security', label: 'Security', types: ['tamper', 'device_offline', 'sensor_fault'] },
  { key: 'emergency', label: 'Emergency', severities: ['critical'] },
]
const activeCat = ref('all')
const activeCatLabel = computed(() => (CATEGORIES.find((c) => c.key === activeCat.value)?.label || '').toLowerCase())

function matchesCategory(a, c) {
  if (c.key === 'all') return true
  if (c.types) return c.types.includes(a.type)
  if (c.severities) return c.severities.includes(a.severity)
  return true
}
function countFor(c) { return alerts.value.filter((a) => matchesCategory(a, c)).length }
const filtered = computed(() => {
  const c = CATEGORIES.find((x) => x.key === activeCat.value) || CATEGORIES[0]
  return alerts.value.filter((a) => matchesCategory(a, c))
})
const openCount = computed(() => alerts.value.filter((a) => a.status === 'open').length)

function sev(s) { return s === 'critical' || s === 'warning' ? s : 'info' }
const SEV_ICON = { critical: ShieldAlert, warning: TriangleAlert, info: Info }
const SEV_TONE = { critical: 'ic-red', warning: 'ic-amber', info: 'ic-info' }
const SEV_BADGE = { critical: 'critical', warning: 'warning', info: 'info' }
const SEV_LABEL = { critical: 'Critical', warning: 'Warning', info: 'Info' }
const STATUS_BADGE = { open: 'brand', acknowledged: 'neutral', resolved: 'valid' }
const STATUS_LABEL = { open: 'Open', acknowledged: 'Acknowledged', resolved: 'Resolved' }

onMounted(async () => {
  try { alerts.value = await getMyAlerts() } catch (e) { /* show empty state */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.alert-list { display: grid; gap: 12px; grid-template-columns: minmax(0, 1fr); }
@media (min-width: 1100px) { .alert-list { grid-template-columns: repeat(2, minmax(0, 1fr)); align-items: start; } }

.alert-card { padding: 16px; border-left: 4px solid var(--border-strong); display: flex; flex-direction: column; gap: 12px; }
.alert-card.sev-critical { border-left-color: var(--crit); }
.alert-card.sev-warning { border-left-color: var(--amber); }
.alert-card.sev-info { border-left-color: var(--info); }
.ac-top { display: flex; align-items: flex-start; gap: 12px; }
.ac-main { flex: 1; min-width: 0; }
.ac-title { font-weight: 800; font-size: 1rem; color: var(--ink-strong); line-height: 1.3; }
.ac-meta { color: var(--muted); font-size: .8125rem; font-weight: 600; margin-top: 3px; }
.ac-meta .sep { margin: 0 6px; color: var(--muted-2); }
.ac-msg { color: var(--text); font-size: .9375rem; line-height: 1.5; }
.ac-foot { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding-top: 12px; border-top: 1px solid var(--border); }
.ac-when { font-size: .8125rem; }
.ac-map { margin: -4px -8px -4px 0; color: var(--info); }
@media (max-width: 400px) { .ac-when { display: none; } }
</style>
