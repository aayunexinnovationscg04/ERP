<template>
  <div class="topbar">
    <h1>Fuel Efficiency Analytics</h1>
    <span class="muted">{{ leaderboard.length }} truck(s) ranked</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-green hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg green ic"><TrendingUp :size="20" class="icon-lg" /></span><div class="n">{{ fmt(fleetAvg) }}</div><div class="l">Fleet avg km/L</div>
    </motion.div>
    <motion.div class="card kpi glow-blue" :while-hover="{ y: -2 }">
      <span class="icon-chip lg blue ic"><Trophy :size="20" class="icon-lg" /></span><div class="n">{{ best?.name || '—' }}</div><div class="l">Best performer</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><TrendingDown :size="20" class="icon-lg" /></span><div class="n">{{ worst?.name || '—' }}</div><div class="l">Needs attention</div>
    </motion.div>
  </div>

  <p class="section-title">Fleet Efficiency Trend</p>
  <div class="card" style="padding:14px 16px">
    <svg class="spark" :viewBox="`0 0 ${trend.width} ${trend.height}`" preserveAspectRatio="none"
         role="img" aria-label="Fleet average efficiency trend, km per litre">
      <line :x1="0" :y1="trend.base" :x2="trend.width" :y2="trend.base" stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
      <polyline :points="trend.area" fill="var(--green)" fill-opacity="0.14" stroke="none" />
      <polyline :points="trend.line" fill="none" stroke="var(--green)" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
    </svg>
    <div class="row" style="justify-content:space-between;margin-top:6px">
      <span class="muted" style="font-size:12px">6 weeks ago <b style="color:var(--ink-strong)">{{ fmt(trendSeries[0]) }}</b> km/L</span>
      <span class="muted" style="font-size:12px">This week <b style="color:var(--ink-strong)">{{ fmt(trendSeries[trendSeries.length - 1]) }}</b> km/L</span>
    </div>
  </div>

  <p class="section-title">Performance Leaderboard</p>
  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Rank</th><th>Truck</th><th>Efficiency</th><th>Distance</th><th>Fuel used</th></tr></thead>
      <tbody>
        <tr v-for="(row, i) in leaderboard" :key="row.id" :class="rankClass(i)">
          <td class="ico">
            <Medal v-if="i < 3" :size="15" :style="{ color: medalColor(i) }" />
            <span v-else class="muted">{{ i + 1 }}</span>
          </td>
          <td style="font-weight:600">{{ row.name }}</td>
          <td><b :style="{ color: row.kmpl >= fleetAvg ? 'var(--green)' : 'var(--amber)' }">{{ fmt(row.kmpl) }} km/L</b></td>
          <td class="muted">{{ fmt(row.distance, 0) }} km</td>
          <td class="muted">{{ fmt(row.fuel, 0) }} L</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { TrendingUp, TrendingDown, Trophy, Medal } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_VEHICLES, seededRandom, range } from '../mock'
import { fmt, sparkline } from '../util'

const rng = seededRandom(606)

const leaderboard = MOCK_VEHICLES.map((v) => {
  const kmpl = range(rng, 3.2, 6.4)
  const distance = range(rng, 1400, 5200)
  return { id: v.id, name: v.name, kmpl, distance, fuel: distance / kmpl }
}).sort((a, b) => b.kmpl - a.kmpl)

const fleetAvg = computed(() => leaderboard.reduce((s, r) => s + r.kmpl, 0) / leaderboard.length)
const best = computed(() => leaderboard[0])
const worst = computed(() => leaderboard[leaderboard.length - 1])

function rankClass(i) { return i === 0 ? 'active' : i === leaderboard.length - 1 ? 'critical' : '' }
function medalColor(i) { return ['#e8b93a', '#b8c0cf', '#c98a4e'][i] }

const trendRng = seededRandom(707)
const trendSeries = Array.from({ length: 6 }, () => range(trendRng, fleetAvg.value * 0.85, fleetAvg.value * 1.1))
const trend = computed(() => sparkline(trendSeries, { width: 600, height: 100 }))
</script>
