<template>
  <PageHeader preview />

  <div class="kpis">
    <StatTile label="Average score" :value="fmt(avgScore, 0)" unit="/ 100" :icon="Gauge" tone="blue" />
    <StatTile label="Overspeed events" :value="totalOverspeed" :icon="Zap" tone="amber" />
    <StatTile label="Behavior flags" :value="totalFlags" :icon="Flag" tone="crit" />
  </div>

  <div class="card flush">
    <div class="card-head"><div class="card-head-title"><Users :size="17" /><h2>Pilot scores</h2></div>
      <div class="map-legend"><span><i class="swatch" style="background:var(--green)"></i>85+ good</span><span><i class="swatch" style="background:var(--amber)"></i>70–84 fair</span><span><i class="swatch" style="background:var(--crit)"></i>&lt;70 coach</span></div></div>
    <div class="table-wrap">
      <table class="mstack">
        <thead><tr><th>Pilot</th><th>Score</th><th class="num">Overspeed</th><th class="num">Harsh braking</th><th>Flags</th></tr></thead>
        <tbody>
          <tr v-for="p in pager.rows.value" :key="p.name">
            <td class="cell-head cell-main nowrap">{{ p.name }}</td>
            <td data-label="Score">
              <div class="pp-score">
                <div class="meter"><span :class="barClass[p.rowClass]" :style="{ width: p.score + '%' }"></span></div>
                <b class="num">{{ p.score }}</b>
              </div>
            </td>
            <td class="num" data-label="Overspeed">{{ p.overspeed }}</td>
            <td class="num" data-label="Harsh braking">{{ p.harshBraking }}</td>
            <td data-label="Flags" class="cell-full" :class="{ 'cell-hide-sm': !p.flags.length }">
              <span v-if="!p.flags.length" class="muted">—</span>
              <span v-else class="pp-flags"><span v-for="f in p.flags" :key="f" class="badge plain critical">{{ f }}</span></span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Gauge, Zap, Flag, Users } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { MOCK_PILOTS, seededRandom, rangeInt, pick } from '../mock'
import { fmt } from '../util'

const FLAG_POOL = ['Harsh braking', 'Sharp turns', 'Night driving', 'Idle overuse', 'Route deviation']
const rng = seededRandom(909)

const pilots = MOCK_PILOTS.map((name) => {
  const overspeed = rangeInt(rng, 0, 9)
  const harshBraking = rangeInt(rng, 0, 6)
  const score = Math.max(48, Math.min(99, Math.round(98 - overspeed * 3.2 - harshBraking * 2.1)))
  const flagCount = score < 70 ? rangeInt(rng, 1, 3) : score < 85 ? rangeInt(rng, 0, 1) : 0
  const flags = []
  const pool = [...FLAG_POOL]
  for (let i = 0; i < flagCount; i++) flags.push(pool.splice(Math.floor(rng() * pool.length), 1)[0])
  const rowClass = score >= 85 ? 'active' : score >= 70 ? 'idle' : 'critical'
  return { name, score, overspeed, harshBraking, flags, rowClass }
}).sort((a, b) => b.score - a.score)

const pager = usePaging(computed(() => pilots), 10)
const barClass = { active: 'green', idle: 'amber', critical: 'crit' }
const avgScore = computed(() => pilots.reduce((s, p) => s + p.score, 0) / pilots.length)
const totalOverspeed = computed(() => pilots.reduce((s, p) => s + p.overspeed, 0))
const totalFlags = computed(() => pilots.reduce((s, p) => s + p.flags.length, 0))
</script>
<style scoped>
.pp-score { display: flex; align-items: center; gap: 10px; min-width: 140px; }
.pp-score .meter { width: 100px; flex: none; }
.pp-score b { color: var(--ink-strong); }
.pp-flags { display: flex; flex-wrap: wrap; gap: 4px; }
@media (max-width: 720px) {
  table.mstack tbody tr { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .pp-score { min-width: 0; gap: 6px; width: 100%; }
  .pp-score .meter { width: auto; flex: 1; }
}
</style>
