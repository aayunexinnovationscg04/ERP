<template>
  <PageHeader preview />

  <div class="kpis">
    <StatTile label="Fleet average" :value="fmt(fleetAvg)" unit="km/L" :icon="TrendingUp" tone="green" />
    <StatTile label="Best performer" :value="best?.name || '—'" :icon="Trophy" tone="blue" />
    <StatTile label="Needs attention" :value="worst?.name || '—'" :icon="TrendingDown" tone="amber" />
  </div>

  <div class="card">
    <div class="card-head"><div class="card-head-title"><Activity :size="17" /><h2>Fleet km/L · last 6 weeks</h2></div></div>
    <div class="card-body">
      <svg class="spark" :viewBox="`0 0 ${trend.width} ${trend.height}`" preserveAspectRatio="none"
           role="img" aria-label="Fleet average efficiency trend, km per litre">
        <line :x1="0" :y1="trend.base" :x2="trend.width" :y2="trend.base" stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
        <polyline :points="trend.area" fill="var(--green)" fill-opacity="0.12" stroke="none" />
        <polyline :points="trend.line" fill="none" stroke="var(--green)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke" />
      </svg>
      <div class="legend-row">
        <span>6 weeks ago <b>{{ fmt(trendSeries[0]) }}</b> km/L</span>
        <span>This week <b>{{ fmt(trendSeries[trendSeries.length - 1]) }}</b> km/L</span>
      </div>
    </div>
  </div>

  <div class="card flush section">
    <div class="card-head"><div class="card-head-title"><Trophy :size="17" /><h2>Leaderboard</h2></div></div>
    <div class="table-wrap">
      <table class="mstack">
        <thead><tr><th style="width:64px">Rank</th><th>Truck</th><th>Efficiency</th><th class="num">Distance</th><th class="num">Fuel used</th></tr></thead>
        <tbody>
          <tr v-for="row in pager.rows.value" :key="row.id">
            <td class="cell-hide-sm"><span class="rank" :class="{ top: row.rank <= 3 }">{{ row.rank }}</span></td>
            <td class="cell-head cell-main nowrap"><span class="ef-name"><span class="rank show-sm" :class="{ top: row.rank <= 3 }">{{ row.rank }}</span>{{ row.name }}</span>
              <b class="num show-sm" :style="{ color: row.kmpl >= fleetAvg ? 'var(--green)' : 'var(--amber)' }">{{ fmt(row.kmpl) }} km/L</b></td>
            <td class="cell-hide-sm">
              <div class="eff">
                <div class="meter" style="flex:1;max-width:160px"><span :class="row.kmpl >= fleetAvg ? 'green' : 'amber'" :style="{ width: (row.kmpl / maxKmpl * 100) + '%' }"></span></div>
                <b class="num" :style="{ color: row.kmpl >= fleetAvg ? 'var(--green)' : 'var(--amber)' }">{{ fmt(row.kmpl) }} km/L</b>
              </div>
            </td>
            <td data-label="Distance" class="num muted">{{ fmt(row.distance, 0) }} km</td>
            <td data-label="Fuel used" class="num muted">{{ fmt(row.fuel, 0) }} L</td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { TrendingUp, TrendingDown, Trophy, Activity } from 'lucide-vue-next'
import { MOCK_VEHICLES, seededRandom, range } from '../mock'
import { fmt, sparkline } from '../util'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const rng = seededRandom(606)
const leaderboard = MOCK_VEHICLES.map((v) => {
  const kmpl = range(rng, 3.2, 6.4)
  const distance = range(rng, 1400, 5200)
  return { id: v.id, name: v.name, kmpl, distance, fuel: distance / kmpl }
}).sort((a, b) => b.kmpl - a.kmpl).map((r, i) => ({ ...r, rank: i + 1 }))
const pager = usePaging(ref(leaderboard), 10)

const fleetAvg = computed(() => leaderboard.reduce((s, r) => s + r.kmpl, 0) / leaderboard.length)
const maxKmpl = Math.max(...leaderboard.map((r) => r.kmpl))
const best = computed(() => leaderboard[0])
const worst = computed(() => leaderboard[leaderboard.length - 1])

const trendRng = seededRandom(707)
const trendSeries = Array.from({ length: 6 }, () => range(trendRng, fleetAvg.value * 0.85, fleetAvg.value * 1.1))
const trend = computed(() => sparkline(trendSeries, { width: 600, height: 100 }))
</script>

<style scoped>
.rank { display: inline-grid; place-items: center; width: 26px; height: 26px; border-radius: 6px; font-size: 12.5px; font-weight: 800; background: var(--surface-3); color: var(--muted); }
.rank.top { background: var(--brand-soft); color: var(--brand-soft-ink); }
.eff { display: flex; align-items: center; gap: 12px; min-width: 180px; }
.eff b { white-space: nowrap; font-size: 13px; }
.ef-name { display: inline-flex; align-items: center; gap: 10px; }
.section { margin-top: 12px; }
@media (max-width: 720px) { .eff { min-width: 0; width: 100%; } .eff .meter { max-width: none !important; } }
</style>
