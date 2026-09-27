<template>
  <PageHeader title="Consumption Reports" description="Litres consumed per truck and across the fleet for the selected period." preview>
    <div class="seg" role="group" aria-label="Period">
      <button :class="{ on: period === 7 }" @click="period = 7">Last 7 days</button>
      <button :class="{ on: period === 30 }" @click="period = 30">Last 30 days</button>
    </div>
  </PageHeader>

  <div class="kpis">
    <StatTile label="Total consumed" :value="fmt(totalLitres, 0)" unit="L" :icon="Fuel" tone="brand" :sub="`Last ${period} days`" />
    <StatTile label="Average per truck" :value="fmt(avgPerTruck, 0)" unit="L" :icon="Gauge" tone="blue" />
    <StatTile label="Highest consumer" :value="topConsumer?.name || '—'" :icon="TrendingUp" tone="amber" :sub="topConsumer ? fmt(topConsumer.litres, 0) + ' L' : ''" />
  </div>

  <div class="card">
    <div class="card-head"><div class="card-head-title"><BarChart3 :size="17" /><div><h2>Consumption per truck</h2>
      <div class="card-sub">Litres, last {{ period }} days</div></div></div></div>
    <div class="card-body">
      <div class="fr-list">
        <div class="fr-row" v-for="row in sorted" :key="row.id">
          <span class="fr-name">{{ row.name }}</span>
          <div class="fr-track"><span :class="{ top: row.id === topConsumer?.id }" :style="{ width: (row.litres / maxLitres * 100) + '%' }"></span></div>
          <b class="fr-val num">{{ fmt(row.litres, 0) }} L</b>
        </div>
      </div>
    </div>
  </div>

  <div class="card section">
    <div class="card-head"><div class="card-head-title"><Activity :size="17" /><div><h2>Daily consumption trend</h2>
      <div class="card-sub">Fleet-wide litres per day, {{ period === 7 ? 'past week' : 'past month' }}</div></div></div></div>
    <div class="card-body">
      <svg class="spark" style="height:140px" :viewBox="`0 0 ${trend.width} ${trend.height}`" preserveAspectRatio="none"
           role="img" aria-label="Fleet-wide fuel consumption trend">
        <line :x1="0" :y1="trend.base" :x2="trend.width" :y2="trend.base" stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
        <polyline :points="trend.area" fill="var(--info)" fill-opacity="0.12" stroke="none" />
        <polyline :points="trend.line" fill="none" stroke="var(--info)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
      </svg>
      <div class="legend-row"><span>{{ period }} days ago</span><span>Today</span></div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Fuel, Gauge, TrendingUp, BarChart3, Activity } from 'lucide-vue-next'
import { MOCK_VEHICLES, seededRandom, range } from '../mock'
import { fmt, sparkline } from '../util'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'

const period = ref(7)

const perVehicle = computed(() => {
  const rng = seededRandom(404 + period.value)
  return MOCK_VEHICLES.map((v) => ({
    id: v.id, name: v.name,
    litres: Math.round(range(rng, period.value === 7 ? 90 : 340, period.value === 7 ? 260 : 980)),
  }))
})
const sorted = computed(() => [...perVehicle.value].sort((a, b) => b.litres - a.litres))
const maxLitres = computed(() => Math.max(...perVehicle.value.map((r) => r.litres), 1))
const totalLitres = computed(() => perVehicle.value.reduce((s, r) => s + r.litres, 0))
const avgPerTruck = computed(() => totalLitres.value / perVehicle.value.length)
const topConsumer = computed(() => sorted.value[0])

const trend = computed(() => {
  const rng = seededRandom(505 + period.value)
  const days = period.value
  const base = totalLitres.value / days
  const series = Array.from({ length: days }, () => range(rng, base * 0.75, base * 1.25))
  return sparkline(series, { width: 600, height: 110 })
})
</script>

<style scoped>
.fr-list { display: flex; flex-direction: column; gap: 12px; }
.fr-row { display: grid; grid-template-columns: 130px minmax(0, 1fr) 70px; align-items: center; gap: 12px; }
.fr-name { font-size: 13px; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fr-track { height: 12px; border-radius: 4px; background: var(--surface-3); overflow: hidden; }
.fr-track span { display: block; height: 100%; border-radius: 4px; background: var(--info); transition: width .3s var(--ease); }
.fr-track span.top { background: var(--brand); }
.fr-val { text-align: right; font-size: 13px; color: var(--ink-strong); }
@media (max-width: 480px) { .fr-row { grid-template-columns: 96px minmax(0, 1fr) 60px; gap: 8px; } }
</style>
