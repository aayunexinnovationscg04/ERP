<template>
  <PageHeader title="Route Optimization" description="Suggested route changes per truck with the time and fuel they could save each week." preview />

  <div class="kpis">
    <StatTile label="Time saved / week" :value="fmt(totalTimeSaved, 0)" unit="min" :icon="Clock" tone="green" />
    <StatTile label="Fuel saved / week" :value="fmt(totalFuelSaved, 0)" unit="L" :icon="Fuel" tone="brand" />
    <StatTile label="Suggestions" :value="suggestions.length" :icon="Compass" tone="blue" />
  </div>

  <div class="card flush">
    <div class="list">
      <div class="list-row ro-row" v-for="s in suggestions" :key="s.id">
        <span class="icon-chip blue"><Route :size="17" /></span>
        <div class="grow">
          <div class="ro-head"><b>{{ s.vehicleName }}</b><span class="muted">{{ s.from }} → {{ s.to }}</span></div>
          <p class="ro-desc">{{ s.suggestion }}</p>
          <div class="ro-savings">
            <span class="badge active plain"><Clock :size="12" /> Save {{ s.timeSaved }} min</span>
            <span class="badge brand plain"><Fuel :size="12" /> Save {{ fmt(s.fuelSaved, 1) }} L</span>
            <span class="muted" style="font-size:12px">{{ s.confidence }}% confidence</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Clock, Fuel, Compass, Route } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
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
.ro-row { align-items: flex-start; padding: 16px 18px; }
.ro-head { display: flex; align-items: baseline; gap: 4px 10px; flex-wrap: wrap; font-size: 14px; }
.ro-head b { color: var(--ink-strong); }
.ro-head .muted { font-size: 13px; }
.ro-desc { font-size: 13px; margin: 4px 0 10px; color: var(--text); }
.ro-savings { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
</style>
