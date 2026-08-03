<template>
  <div class="topbar">
    <h1>Alerts</h1>
    <div class="row seg">
      <button :class="{ primary: filter === 'open' }" @click="setFilter('open')">Open</button>
      <button :class="{ primary: filter === '' }" @click="setFilter('')">All</button>
    </div>
  </div>

  <div class="row chips" style="margin:-6px 0 16px">
    <button type="button" class="chip" :class="{ active: typeFilter === '' }" @click="typeFilter = ''">
      All types
    </button>
    <button type="button" class="chip" v-for="c in TYPE_CATEGORIES" :key="c.type" :class="[c.hue, { active: typeFilter === c.type }]" @click="typeFilter = typeFilter === c.type ? '' : c.type">
      <component :is="c.icon" :size="13" /> {{ c.label }}
      <span class="chip-count">{{ typeCounts[c.type] || 0 }}</span>
    </button>
  </div>

  <p v-if="!canWrite" class="viewonly" style="margin:-8px 0 14px"><Lock :size="14" /> View-only — ask an admin to enable editing.</p>

  <div v-if="loading" class="kpis">
    <div class="skel sk-chip" v-for="n in 3" :key="n"></div>
  </div>
  <div v-else class="kpis">
    <motion.div class="card kpi glow-crit" :while-hover="{ y: -2 }">
      <span class="icon-chip lg crit ic"><TriangleAlert :size="20" class="icon-lg" /></span><div class="n">{{ criticalCount }}</div><div class="l">Critical</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><TriangleAlert :size="20" class="icon-lg" /></span><div class="n">{{ warningCount }}</div><div class="l">Warning</div>
    </motion.div>
    <motion.div class="card kpi glow-blue" :while-hover="{ y: -2 }">
      <span class="icon-chip lg blue ic"><Info :size="20" class="icon-lg" /></span><div class="n">{{ infoCount }}</div><div class="l">Info</div>
    </motion.div>
  </div>

  <div v-if="loading" style="padding:2px 0">
    <div class="skel sk-row" v-for="n in 5" :key="n"></div>
  </div>

  <div v-else class="card" style="padding:6px 0">
    <table>
      <thead>
        <tr><th>Severity</th><th>Type</th><th>Title</th><th>Vehicle</th><th>When</th><th></th></tr>
      </thead>
      <tbody>
        <motion.tr v-for="(a, i) in filteredAlerts" :key="a.id" :class="a.severity"
          :initial="{ opacity: 0, y: 6 }" :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: .2, delay: Math.min(i, 12) * .025, ease: [.4, 0, .2, 1] }">
          <td>
            <span class="icon-chip" :class="chipClass[a.severity]">
              <component :is="typeIcon(a.type)" :size="16" />
            </span>
            <span class="badge" :class="a.severity">{{ a.severity }}</span>
          </td>
          <td class="muted">{{ a.type_label || a.type }}</td>
          <td>{{ a.title }}<div class="muted" style="font-size:12px">{{ a.message }}</div></td>
          <td>{{ a.vehicle_reg || a.device_id || '—' }}</td>
          <td class="muted">{{ ago(a.created_at) }}</td>
          <td>
            <button v-if="a.status === 'open' && canWrite" @click="ack(a)">Acknowledge</button>
            <span v-else class="muted">{{ a.status }}</span>
          </td>
        </motion.tr>
        <tr v-if="!filteredAlerts.length"><td colspan="6" class="muted" style="padding:16px">No alerts{{ typeFilter ? ' in this category' : '' }}.</td></tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { Lock, TriangleAlert, Info, Gauge, MapPin, Fuel, ShieldAlert, Siren, WifiOff, Wrench, PauseCircle } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { getAlerts, ackAlert } from '../api'
import { auth } from '../auth'
import { ago } from '../util'
import { toast } from '../toast'

const canWrite = computed(() => auth.user?.may_write !== false)
const alerts = ref([])
const filter = ref('open')
const loading = ref(true)
const chipClass = { critical: 'crit', warning: 'amber', info: 'blue' }

// Every alert already carries a real category (type) beyond its severity —
// use it to vary the row's icon, not just its color, so a critical overspeed
// row doesn't look identical to a critical fuel-theft row.
const TYPE_ICON = {
  overspeed: Gauge,
  geofence_breach: MapPin,
  low_fuel: Fuel,
  fuel_fill: Fuel,
  fuel_theft: ShieldAlert,
  tamper: Siren,
  device_offline: WifiOff,
  sensor_fault: Wrench,
  idle_too_long: PauseCircle,
}
function typeIcon(type) { return TYPE_ICON[type] || TriangleAlert }

// Category filter chips — the app's scope note calls out five categories
// specifically (Fuel Theft / Low Fuel / Geo Security / Tamper / Overspeed).
// These map straight onto types the alert model already carries; no new
// alert type is invented here, just a lightweight client-side filter on top
// of whatever `load()` already fetched for the current status tab.
const TYPE_CATEGORIES = [
  { type: 'fuel_theft', label: 'Fuel Theft', icon: ShieldAlert, hue: 'crit' },
  { type: 'low_fuel', label: 'Low Fuel', icon: Fuel, hue: 'violet' },
  { type: 'geofence_breach', label: 'Geo Security', icon: MapPin, hue: 'cyan' },
  { type: 'tamper', label: 'Tamper', icon: Siren, hue: 'amber' },
  { type: 'overspeed', label: 'Overspeed', icon: Gauge, hue: 'blue' },
]
const typeFilter = ref('')
const filteredAlerts = computed(() =>
  typeFilter.value ? alerts.value.filter((a) => a.type === typeFilter.value) : alerts.value)
const typeCounts = computed(() => {
  const counts = {}
  for (const a of alerts.value) counts[a.type] = (counts[a.type] || 0) + 1
  return counts
})

const criticalCount = computed(() => filteredAlerts.value.filter((a) => a.severity === 'critical').length)
const warningCount = computed(() => filteredAlerts.value.filter((a) => a.severity === 'warning').length)
const infoCount = computed(() => filteredAlerts.value.filter((a) => a.severity === 'info').length)

async function load() {
  loading.value = true
  try { alerts.value = await getAlerts(filter.value ? { status: filter.value } : {}) }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
function setFilter(f) { filter.value = f; load() }
async function ack(a) {
  try {
    await ackAlert(a.id)
    toast.success('Alert acknowledged')
    load()
  } catch (e) { toast.error('Could not acknowledge alert') }
}

onMounted(load)
</script>

<style scoped>
.seg { background: var(--surface-2); border: 1px solid var(--border); padding: 3px; border-radius: var(--radius-pill); gap: 2px; }
.seg button { border: none; background: none; padding: 7px 16px; border-radius: var(--radius-pill); }
.seg button.primary { box-shadow: none; }
.seg button:not(.primary):hover { background: var(--surface-3); }

.chips { flex-wrap: wrap; gap: 8px; }
.chip {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid var(--border); background: var(--surface-2); color: var(--muted);
  font-size: 12.5px; font-weight: 600; padding: 6px 12px; border-radius: var(--radius-pill);
}
.chip:hover { background: var(--surface-3); color: var(--text); }
.chip-count { font-weight: 700; opacity: .75; }
.chip.active.crit   { background: var(--crit-soft);   color: var(--crit);   border-color: transparent; }
.chip.active.violet { background: var(--violet-soft); color: var(--violet); border-color: transparent; }
.chip.active.cyan   { background: var(--cyan-soft);   color: var(--cyan);   border-color: transparent; }
.chip.active.amber  { background: var(--amber-soft);  color: var(--amber);  border-color: transparent; }
.chip.active.blue   { background: var(--blue-soft);   color: var(--blue);   border-color: transparent; }
</style>
