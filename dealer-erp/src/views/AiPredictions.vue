<template>
  <div class="topbar">
    <h1>AI Predictions</h1>
    <span class="muted ico"><Sparkles :size="13" /> Estimated from recent telemetry &amp; trip patterns</span>
  </div>

  <div class="ai-grid">
    <motion.div class="card ai-box" v-for="(p, i) in predictions" :key="p.id"
                :initial="{ opacity: 0, y: 10 }" :animate="{ opacity: 1, y: 0 }"
                :transition="{ duration: .22, delay: Math.min(i, 12) * .03, ease: [.4, 0, .2, 1] }">
      <div class="ai-box-head">
        <span class="icon-chip blue"><Truck :size="16" /></span>
        <b>{{ p.vehicleName }}</b>
      </div>
      <div class="ai-metric">
        <span class="icon-chip sm green"><Gauge :size="13" /></span>
        <span class="ai-metric-label">Mileage prediction</span>
        <span class="ai-metric-val">{{ fmt(p.mileage) }} km/L</span>
      </div>
      <div class="ai-metric">
        <span class="icon-chip sm violet"><Fuel :size="13" /></span>
        <span class="ai-metric-label">Fuel need (next 7d)</span>
        <span class="ai-metric-val">{{ fmt(p.fuelNeed, 0) }} L</span>
      </div>
      <div class="ai-metric">
        <span class="icon-chip sm amber"><Wrench :size="13" /></span>
        <span class="ai-metric-label">Maintenance due</span>
        <span class="ai-metric-val">{{ p.maintenanceDays }} days</span>
      </div>
      <div class="ai-metric">
        <span class="icon-chip sm crit"><Clock :size="13" /></span>
        <span class="ai-metric-label">Delay risk</span>
        <span class="ai-metric-val" :style="{ color: p.delayRiskColor }">{{ p.delayRisk }}</span>
      </div>
      <p class="muted ai-caveat">Predictive estimate — confidence {{ p.confidence }}%.</p>
    </motion.div>
  </div>
</template>

<script setup>
import { Sparkles, Truck, Gauge, Fuel, Wrench, Clock } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_VEHICLES, seededRandom, range, rangeInt, pick } from '../mock'
import { fmt } from '../util'

const rng = seededRandom(1616)
const RISK = [
  { label: 'Low', color: 'var(--green)' },
  { label: 'Moderate', color: 'var(--amber)' },
  { label: 'High', color: 'var(--crit)' },
]

const predictions = MOCK_VEHICLES.map((v) => {
  const risk = pick(rng, [RISK[0], RISK[0], RISK[1], RISK[2]])
  return {
    id: v.id, vehicleName: v.name,
    mileage: range(rng, 3.4, 6.2),
    fuelNeed: range(rng, 120, 480),
    maintenanceDays: rangeInt(rng, 3, 45),
    delayRisk: risk.label, delayRiskColor: risk.color,
    confidence: rangeInt(rng, 78, 96),
  }
})
</script>

<style scoped>
.ai-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }
.ai-box { padding: 18px 20px; display: flex; flex-direction: column; gap: 10px; }
.ai-box-head { display: flex; align-items: center; gap: 10px; font-size: 15px; color: var(--ink-strong); margin-bottom: 2px; }
.ai-metric { display: flex; align-items: center; gap: 9px; font-size: 13px; }
.ai-metric-label { flex: 1; color: var(--muted); }
.ai-metric-val { font-weight: 700; color: var(--ink-strong); }
.ai-caveat { font-size: 11px; margin: 6px 0 0; padding-top: 8px; border-top: 1px solid var(--border); }
</style>
