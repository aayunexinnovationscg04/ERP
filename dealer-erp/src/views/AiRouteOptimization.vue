<template>
  <div class="topbar">
    <h1>Route Optimization</h1>
    <span class="muted ico"><Sparkles :size="13" /> AI-suggested routes based on traffic &amp; fuel patterns</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-green hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg green ic"><Clock :size="20" class="icon-lg" /></span><div class="n">{{ fmt(totalTimeSaved, 0) }} min</div><div class="l">Potential time saved / week</div>
    </motion.div>
    <motion.div class="card kpi glow-violet" :while-hover="{ y: -2 }">
      <span class="icon-chip lg violet ic"><Fuel :size="20" class="icon-lg" /></span><div class="n">{{ fmt(totalFuelSaved, 0) }} L</div><div class="l">Potential fuel saved / week</div>
    </motion.div>
    <motion.div class="card kpi glow-blue" :while-hover="{ y: -2 }">
      <span class="icon-chip lg blue ic"><Compass :size="20" class="icon-lg" /></span><div class="n">{{ suggestions.length }}</div><div class="l">Suggested routes</div>
    </motion.div>
  </div>

  <div class="ro-list">
    <motion.div class="card ro-row" v-for="(s, i) in suggestions" :key="s.id"
                :initial="{ opacity: 0, y: 8 }" :animate="{ opacity: 1, y: 0 }"
                :transition="{ duration: .2, delay: Math.min(i, 12) * .025, ease: [.4, 0, .2, 1] }">
      <span class="icon-chip lg blue ro-ic"><Route :size="20" class="icon-lg" /></span>
      <div class="ro-body">
        <div class="ro-head">
          <b>{{ s.vehicleName }}</b>
          <span class="muted">{{ s.from }} → {{ s.to }}</span>
        </div>
        <p class="muted ro-desc">{{ s.suggestion }}</p>
        <div class="row ro-savings">
          <span class="badge active ico"><Clock :size="12" /> Save {{ s.timeSaved }} min</span>
          <span class="badge info ico"><Fuel :size="12" /> Save {{ fmt(s.fuelSaved, 1) }} L</span>
          <span class="muted" style="font-size:12px">{{ s.confidence }}% confidence</span>
        </div>
      </div>
    </motion.div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Sparkles, Clock, Fuel, Compass, Route } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_VEHICLES, seededRandom, pick, rangeInt, range } from '../mock'
import { fmt } from '../util'

const rng = seededRandom(1717)
const PLACES = [
  'Depot Yard, Raipur', 'Bhilai Steel Gate', 'Durg Warehouse', 'Rajnandgaon Terminal',
  'Bilaspur Fuel Depot', 'Korba Loading Point', 'Ambikapur Site', 'Jagdalpur Customer Site',
]
const REASONS = [
  'Avoids peak-hour congestion on NH-30 between 5–7pm.',
  'Shorter route via the bypass road cuts 12 signals off the current path.',
  'Alternate route avoids a known low-fuel-efficiency uphill stretch.',
  'Recommended departure shift avoids repeated overspeed-prone segment.',
  'Consolidates two nearby stops into a single loop.',
]

const suggestions = MOCK_VEHICLES.map((v, i) => {
  let from = pick(rng, PLACES)
  let to = pick(rng, PLACES)
  if (to === from) to = PLACES[(PLACES.indexOf(from) + 1) % PLACES.length]
  return {
    id: v.id, vehicleName: v.name, from, to,
    suggestion: pick(rng, REASONS),
    timeSaved: rangeInt(rng, 8, 45),
    fuelSaved: range(rng, 1.5, 9.5),
    confidence: rangeInt(rng, 72, 94),
  }
})

const totalTimeSaved = computed(() => suggestions.reduce((s, r) => s + r.timeSaved, 0))
const totalFuelSaved = computed(() => suggestions.reduce((s, r) => s + r.fuelSaved, 0))
</script>

<style scoped>
.ro-list { display: flex; flex-direction: column; gap: 12px; }
.ro-row { padding: 16px 18px; display: flex; gap: 14px; align-items: flex-start; }
.ro-ic { flex: none; }
.ro-body { flex: 1; min-width: 0; }
.ro-head { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; font-size: 14.5px; }
.ro-desc { font-size: 13px; margin: 4px 0 10px; }
.ro-savings { gap: 10px; flex-wrap: wrap; }
</style>
