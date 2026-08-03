<template>
  <div class="topbar">
    <h1>Consumption Reports</h1>
    <div class="row seg">
      <button :class="{ primary: period === 7 }" @click="period = 7">Last 7 days</button>
      <button :class="{ primary: period === 30 }" @click="period = 30">Last 30 days</button>
    </div>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-violet hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg violet ic"><Fuel :size="20" class="icon-lg" /></span><div class="n">{{ fmt(totalLitres, 0) }}</div><div class="l">Total litres · {{ period }}d</div>
    </motion.div>
    <motion.div class="card kpi glow-blue" :while-hover="{ y: -2 }">
      <span class="icon-chip lg blue ic"><Gauge :size="20" class="icon-lg" /></span><div class="n">{{ fmt(avgPerTruck, 0) }}</div><div class="l">Avg L / truck</div>
    </motion.div>
    <motion.div class="card kpi glow-crit" :while-hover="{ y: -2 }">
      <span class="icon-chip lg crit ic"><TrendingUp :size="20" class="icon-lg" /></span><div class="n">{{ topConsumer?.name || '—' }}</div><div class="l">Highest consumer</div>
    </motion.div>
  </div>

  <p class="section-title">Consumption per truck · last {{ period }} days</p>
  <div class="card" style="padding:20px 22px">
    <div class="fr-chart">
      <div class="fr-bar-col" v-for="row in perVehicle" :key="row.id">
        <div class="fr-bar-track">
          <div class="fr-bar-fill" :style="{ height: (row.litres / maxLitres * 100) + '%' }"></div>
        </div>
        <div class="fr-bar-val">{{ fmt(row.litres, 0) }}L</div>
        <div class="muted fr-bar-label">{{ row.name }}</div>
      </div>
    </div>
  </div>

  <p class="section-title">Daily consumption trend</p>
  <div class="card" style="padding:14px 16px">
    <svg class="spark" :viewBox="`0 0 ${trend.width} ${trend.height}`" preserveAspectRatio="none"
         role="img" aria-label="Fleet-wide fuel consumption trend">
      <line :x1="0" :y1="trend.base" :x2="trend.width" :y2="trend.base" stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
      <polyline :points="trend.area" fill="var(--violet)" fill-opacity="0.14" stroke="none" />
      <polyline :points="trend.line" fill="none" stroke="var(--violet)" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
    </svg>
    <p class="muted" style="margin:6px 0 0;font-size:12px">Fleet-wide litres consumed per day, {{ period === 7 ? 'past week' : 'past month' }}.</p>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Fuel, Gauge, TrendingUp } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_VEHICLES, seededRandom, range } from '../mock'
import { fmt, sparkline } from '../util'

const period = ref(7)

const perVehicle = computed(() => {
  const rng = seededRandom(404 + period.value)
  return MOCK_VEHICLES.map((v) => ({
    id: v.id, name: v.name,
    litres: Math.round(range(rng, period.value === 7 ? 90 : 340, period.value === 7 ? 260 : 980)),
  }))
})
const maxLitres = computed(() => Math.max(...perVehicle.value.map((r) => r.litres), 1))
const totalLitres = computed(() => perVehicle.value.reduce((s, r) => s + r.litres, 0))
const avgPerTruck = computed(() => totalLitres.value / perVehicle.value.length)
const topConsumer = computed(() => [...perVehicle.value].sort((a, b) => b.litres - a.litres)[0])

const trend = computed(() => {
  const rng = seededRandom(505 + period.value)
  const days = period.value
  const base = totalLitres.value / days
  const series = Array.from({ length: days }, () => range(rng, base * 0.75, base * 1.25))
  return sparkline(series, { width: 600, height: 110 })
})
</script>

<style scoped>
.seg { background: var(--surface-2); border: 1px solid var(--border); padding: 3px; border-radius: var(--radius-pill); gap: 2px; }
.seg button { border: none; background: none; padding: 7px 16px; border-radius: var(--radius-pill); }
.seg button.primary { box-shadow: none; }
.seg button:not(.primary):hover { background: var(--surface-3); }

.fr-chart { display: flex; align-items: flex-end; gap: 14px; height: 200px; overflow-x: auto; }
.fr-bar-col { display: flex; flex-direction: column; align-items: center; gap: 6px; flex: 1 0 64px; min-width: 64px; height: 100%; }
.fr-bar-track { flex: 1; width: 100%; max-width: 40px; display: flex; align-items: flex-end; background: var(--surface-2); border-radius: 8px 8px 4px 4px; overflow: hidden; }
.fr-bar-fill { width: 100%; background: var(--grad-violet); border-radius: 8px 8px 0 0; transition: height var(--dur) var(--ease); min-height: 3px; }
.fr-bar-val { font-size: 12px; font-weight: 700; color: var(--ink-strong); }
.fr-bar-label { font-size: 11px; text-align: center; }
</style>
