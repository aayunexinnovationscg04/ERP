<template>
  <PageHeader title="AI Predictions" description="Estimated mileage, fuel need, maintenance timing and delay risk per truck." preview />

  <div class="ai-grid">
    <div class="card ai-box" v-for="p in predictions" :key="p.id">
      <div class="ai-box-head">
        <span class="icon-chip blue"><Truck :size="16" /></span>
        <b>{{ p.vehicleName }}</b>
        <span class="badge" :class="riskBadge[p.delayRisk]" style="margin-left:auto">{{ p.delayRisk }} risk</span>
      </div>
      <div class="ai-metrics">
        <div class="ai-metric"><span class="k"><Gauge :size="14" /> Mileage</span><b class="num">{{ fmt(p.mileage) }} km/L</b></div>
        <div class="ai-metric"><span class="k"><Fuel :size="14" /> Fuel need · 7d</span><b class="num">{{ fmt(p.fuelNeed, 0) }} L</b></div>
        <div class="ai-metric"><span class="k"><Wrench :size="14" /> Service due</span><b class="num">{{ p.maintenanceDays }} days</b></div>
        <div class="ai-metric"><span class="k"><Clock :size="14" /> Delay risk</span><b>{{ p.delayRisk }}</b></div>
      </div>
      <div class="ai-conf"><span>Confidence</span><div class="meter" style="flex:1"><span :style="{ width: p.confidence + '%' }"></span></div><b class="num">{{ p.confidence }}%</b></div>
    </div>
  </div>
</template>

<script setup>
import { Truck, Gauge, Fuel, Wrench, Clock } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import { MOCK_VEHICLES, seededRandom, range, rangeInt, pick } from '../mock'
import { fmt } from '../util'

const rng = seededRandom(1616)
const RISK = [
  { label: 'Low', color: 'var(--green)' },
  { label: 'Moderate', color: 'var(--amber)' },
  { label: 'High', color: 'var(--crit)' },
]

const riskBadge = { Low: 'active', Moderate: 'idle', High: 'critical' }
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
.ai-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.ai-box { padding: 16px 18px; display: flex; flex-direction: column; gap: 14px; }
.ai-box-head { display: flex; align-items: center; gap: 10px; font-size: 15px; color: var(--ink-strong); }
.ai-metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.ai-metric { display: flex; flex-direction: column; gap: 2px; }
.ai-metric .k { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); font-weight: 600; }
.ai-metric b { font-size: 15px; color: var(--ink-strong); }
.ai-conf { display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--muted); padding-top: 12px; border-top: 1px solid var(--border); }
.ai-conf b { color: var(--text); }
</style>
