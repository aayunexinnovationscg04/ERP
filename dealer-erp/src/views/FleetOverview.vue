<template>
  <div class="topbar">
    <h1>Fleet Overview</h1>
    <span class="muted">{{ MOCK_VEHICLES.length }} truck(s) in fleet</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-blue hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg blue ic"><Truck :size="20" class="icon-lg" /></span><div class="n">{{ totalTrucks }}</div><div class="l">Total trucks</div>
    </motion.div>
    <motion.div class="card kpi glow-green" :while-hover="{ y: -2 }">
      <span class="icon-chip lg green ic"><Navigation :size="20" class="icon-lg" /></span><div class="n">{{ activeTrucks }}</div><div class="l">Active trucks</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><PauseCircle :size="20" class="icon-lg" /></span><div class="n">{{ idleTrucks }}</div><div class="l">Idle trucks</div>
    </motion.div>
  </div>

  <p class="section-title">Truck Health Status</p>
  <div class="card fo-health">
    <svg class="fo-donut" viewBox="0 0 120 120" role="img" aria-label="Truck health breakdown">
      <circle cx="60" cy="60" r="46" fill="none" stroke="var(--surface-3)" stroke-width="16" />
      <circle v-for="seg in donutSegs" :key="seg.label" cx="60" cy="60" r="46" fill="none"
              :stroke="seg.color" stroke-width="16" stroke-linecap="butt"
              :stroke-dasharray="`${seg.dash} ${circumference - seg.dash}`"
              :stroke-dashoffset="seg.offset" transform="rotate(-90 60 60)" />
      <text x="60" y="56" text-anchor="middle" class="fo-donut-n">{{ totalTrucks }}</text>
      <text x="60" y="72" text-anchor="middle" class="fo-donut-l">trucks</text>
    </svg>
    <div class="fo-legend">
      <div class="fo-legend-row" v-for="seg in donutSegs" :key="seg.label">
        <span class="dot" :class="seg.dot"></span>
        <span class="fo-legend-label">{{ seg.label }}</span>
        <span class="fo-legend-n">{{ seg.count }}</span>
        <span class="muted fo-legend-pct">{{ Math.round((seg.count / totalTrucks) * 100) }}%</span>
      </div>
      <p class="muted fo-note">Based on latest telemetry, document expiry and maintenance signals across the fleet.</p>
    </div>
  </div>

  <p class="section-title">Fleet Roster</p>
  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Truck</th><th>Status</th><th>Health</th></tr></thead>
      <tbody>
        <tr v-for="row in roster" :key="row.id" :class="row.statusClass">
          <td>
            <span class="row-with-chip">
              <span class="icon-chip" :class="row.statusClass === 'active' ? 'green' : 'amber'"><Truck :size="16" /></span>
              <span>
                <div style="font-weight:600">{{ row.name }}</div>
                <div class="muted" style="font-size:12px">{{ row.reg }}</div>
              </span>
            </span>
          </td>
          <td><span class="badge" :class="row.statusClass">{{ row.status }}</span></td>
          <td><span class="badge" :class="row.healthBadge">{{ row.health }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Truck, Navigation, PauseCircle } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_VEHICLES, seededRandom, pick } from '../mock'

const rng = seededRandom(101)
const totalTrucks = MOCK_VEHICLES.length

const roster = MOCK_VEHICLES.map((v) => {
  const active = rng() > 0.28
  const health = pick(rng, ['good', 'good', 'good', 'warning', 'critical'])
  return {
    ...v,
    status: active ? 'Active' : 'Idle',
    statusClass: active ? 'active' : 'idle',
    health: health === 'good' ? 'Good' : health === 'warning' ? 'Warning' : 'Critical',
    healthBadge: health === 'good' ? 'active' : health === 'warning' ? 'idle' : 'critical',
  }
})

const activeTrucks = computed(() => roster.filter((r) => r.statusClass === 'active').length)
const idleTrucks = computed(() => roster.filter((r) => r.statusClass === 'idle').length)

const healthCounts = computed(() => ({
  good: roster.filter((r) => r.health === 'Good').length,
  warning: roster.filter((r) => r.health === 'Warning').length,
  critical: roster.filter((r) => r.health === 'Critical').length,
}))

const circumference = 2 * Math.PI * 46
const donutSegs = computed(() => {
  const c = healthCounts.value
  const defs = [
    { key: 'good', label: 'Good', count: c.good, color: 'var(--green)', dot: 'green' },
    { key: 'warning', label: 'Warning', count: c.warning, color: 'var(--amber)', dot: 'amber' },
    { key: 'critical', label: 'Critical', count: c.critical, color: 'var(--crit)', dot: 'red' },
  ]
  let acc = 0
  return defs.filter((d) => d.count > 0).map((d) => {
    const dash = (d.count / totalTrucks) * circumference
    const seg = { ...d, dash, offset: -acc }
    acc += dash
    return seg
  })
})
</script>

<style scoped>
.fo-health { padding: 20px 22px; display: flex; align-items: center; gap: 28px; flex-wrap: wrap; }
.fo-donut { width: 148px; height: 148px; flex: none; }
.fo-donut-n { fill: var(--ink-strong); font-size: 22px; font-weight: 800; font-family: var(--font-head); }
.fo-donut-l { fill: var(--muted); font-size: 9px; text-transform: uppercase; letter-spacing: .06em; }
.fo-legend { flex: 1; min-width: 200px; display: flex; flex-direction: column; gap: 8px; }
.fo-legend-row { display: flex; align-items: center; gap: 8px; font-size: 14px; }
.fo-legend-label { font-weight: 600; flex: 1; }
.fo-legend-n { font-weight: 800; color: var(--ink-strong); }
.fo-legend-pct { width: 40px; text-align: right; font-size: 12px; }
.fo-note { font-size: 12px; margin: 6px 0 0; }

@media (max-width: 560px) {
  .fo-health { flex-direction: column; align-items: flex-start; }
}
</style>
