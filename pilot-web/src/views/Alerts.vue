<template>
  <template v-if="loading">
    <div class="kpis"><div class="skel sk-chip" v-for="n in 3" :key="n"></div></div>
    <div class="skel sk-row" v-for="n in 5" :key="'r'+n"></div>
  </template>

  <div v-else-if="!alerts.length" class="card">
    <EmptyState :icon="ShieldCheck" title="All clear" text="No alerts for your truck." />
  </div>

  <template v-else>
    <div class="kpis alert-kpis">
      <StatTile label="Open" :value="openCount" :icon="Bell" tone="brand" />
      <StatTile label="Critical" :value="critCount" :icon="Siren" tone="crit" />
      <StatTile label="Total" :value="alerts.length" :icon="ShieldAlert" tone="blue" />
    </div>

    <div class="card flush">
      <div class="card-head">
        <div class="toolbar al-toolbar">
          <div class="chips" role="group" aria-label="Filter alerts">
            <button v-for="c in shownCats" :key="c.key" type="button" class="chip" :class="{ on: activeCat === c.key }"
              :aria-pressed="activeCat === c.key" @click="activeCat = c.key">
              {{ c.label }}<span class="chip-count">{{ countFor(c) }}</span>
            </button>
          </div>
        </div>
      </div>

      <EmptyState v-if="!filtered.length" :icon="CircleCheck" :title="`No ${activeCatLabel} alerts`">
        <button type="button" @click="activeCat = 'all'">Show all</button>
      </EmptyState>

      <template v-else>
        <div class="list">
          <article v-for="a in pager.rows.value" :key="a.id" class="list-row alert-card" :class="'sev-' + sev(a.severity)">
            <span class="icon-chip" :class="SEV_TONE[sev(a.severity)]"><component :is="SEV_ICON[sev(a.severity)]" :size="16" /></span>
            <div class="grow">
              <div class="al-top">
                <span class="title">{{ a.title || a.type_label || a.type }}</span>
                <span class="badge" :class="SEV_BADGE[sev(a.severity)]">{{ SEV_LABEL[sev(a.severity)] }}</span>
              </div>
              <p v-if="a.message" class="al-body">{{ a.message }}</p>
              <div class="al-foot">
                <span class="sub">
                  <template v-if="a.title && a.type_label && !a.title.toLowerCase().includes(a.type_label.toLowerCase())">{{ a.type_label }} · </template>
                  <time :datetime="a.created_at" :title="dateTime(a.created_at)">{{ timeAgo(a.created_at) }}</time>
                </span>
                <span class="spacer"></span>
                <a v-if="a.lat != null && a.lng != null" class="btn sm ghost al-map"
                  :href="`https://www.google.com/maps/search/?api=1&query=${a.lat},${a.lng}`" target="_blank" rel="noopener">
                  <MapPin :size="14" /> Location
                </a>
                <span class="badge plain al-status" :class="STATUS_BADGE[a.status] || 'gray'">{{ STATUS_LABEL[a.status] || a.status }}</span>
              </div>
            </div>
          </article>
        </div>
        <Pager :pager="pager" />
      </template>
    </div>
  </template>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { CircleCheck, TriangleAlert, ShieldAlert, Info, ShieldCheck, MapPin, Bell, Siren } from 'lucide-vue-next'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { getMyAlerts } from '../api'
import { timeAgo, dateTime } from '../format'

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
// Hide empty categories (the active one stays so it can be switched off).
const shownCats = computed(() => CATEGORIES.filter((c) => c.key === 'all' || c.key === activeCat.value || countFor(c) > 0))
function countFor(c) { return alerts.value.filter((a) => matchesCategory(a, c)).length }
const filtered = computed(() => {
  const c = CATEGORIES.find((x) => x.key === activeCat.value) || CATEGORIES[0]
  return alerts.value.filter((a) => matchesCategory(a, c))
})
const pager = usePaging(filtered, 10, [activeCat])
const openCount = computed(() => alerts.value.filter((a) => a.status === 'open').length)
const critCount = computed(() => alerts.value.filter((a) => a.severity === 'critical').length)

function sev(s) { return s === 'critical' || s === 'warning' ? s : 'info' }
const SEV_ICON = { critical: ShieldAlert, warning: TriangleAlert, info: Info }
const SEV_TONE = { critical: 'crit', warning: 'amber', info: 'info' }
const SEV_BADGE = { critical: 'critical', warning: 'warning', info: 'info' }
const SEV_LABEL = { critical: 'Critical', warning: 'Warning', info: 'Info' }
const STATUS_BADGE = { open: 'brand', acknowledged: 'gray', resolved: 'green' }
const STATUS_LABEL = { open: 'Open', acknowledged: 'Acknowledged', resolved: 'Resolved' }

onMounted(async () => {
  try { alerts.value = await getMyAlerts() } catch (e) { /* show empty state */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.al-toolbar { margin: 0; width: 100%; }
.alert-card { align-items: flex-start; }
.alert-card .icon-chip { margin-top: 1px; }
.al-top { display: flex; align-items: center; gap: 10px; justify-content: space-between; min-width: 0; }
.al-top .title { white-space: normal; }
.al-body { margin-top: 3px; font-size: 13.5px; color: var(--text); }
.al-foot { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-top: 6px; min-width: 0; }
.al-foot .sub { white-space: normal; }
.al-map { color: var(--info); }
</style>
