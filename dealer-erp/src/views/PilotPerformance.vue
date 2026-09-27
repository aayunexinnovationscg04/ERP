<template>
  <PageHeader title="Performance & Behavior" description="Driving score per pilot from overspeed and harsh-braking events this month." preview />

  <div class="kpis">
    <StatTile label="Average score" :value="fmt(avgScore, 0)" unit="/ 100" :icon="Gauge" tone="blue" />
    <StatTile label="Overspeed events" :value="totalOverspeed" :icon="Zap" tone="amber" />
    <StatTile label="Behavior flags" :value="totalFlags" :icon="Flag" tone="crit" />
  </div>

  <div class="card flush">
    <div class="card-head"><div class="card-head-title"><Users :size="17" /><div><h2>Pilot scores</h2>
      <div class="card-sub">85+ good · 70–84 fair · below 70 needs coaching</div></div></div></div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Pilot</th><th>Score</th><th class="num hide-sm">Overspeed</th><th class="num hide-sm">Harsh braking</th><th>Flags</th></tr></thead>
        <tbody>
          <tr v-for="p in pilots" :key="p.name">
            <td class="cell-main nowrap">{{ p.name }}</td>
            <td>
              <div class="pp-score">
                <div class="meter"><span :class="barClass[p.rowClass]" :style="{ width: p.score + '%' }"></span></div>
                <b class="num">{{ p.score }}</b>
              </div>
            </td>
            <td class="num hide-sm">{{ p.overspeed }}</td>
            <td class="num hide-sm">{{ p.harshBraking }}</td>
            <td>
              <span v-if="!p.flags.length" class="muted">None</span>
              <span v-else class="pp-flags"><span v-for="f in p.flags" :key="f" class="badge plain critical">{{ f }}</span></span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Gauge, Zap, Flag, Users } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
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
</style>
