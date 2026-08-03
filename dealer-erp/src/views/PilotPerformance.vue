<template>
  <div class="topbar">
    <h1>Performance &amp; Behavior</h1>
    <span class="muted">{{ pilots.length }} pilot(s)</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-blue hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg blue ic"><Gauge :size="20" class="icon-lg" /></span><div class="n">{{ fmt(avgScore, 0) }}</div><div class="l">Avg score / 100</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><Zap :size="20" class="icon-lg" /></span><div class="n">{{ totalOverspeed }}</div><div class="l">Overspeed events</div>
    </motion.div>
    <motion.div class="card kpi glow-crit" :while-hover="{ y: -2 }">
      <span class="icon-chip lg crit ic"><Flag :size="20" class="icon-lg" /></span><div class="n">{{ totalFlags }}</div><div class="l">Behavior flags</div>
    </motion.div>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Pilot</th><th>Score</th><th class="col-optional">Overspeed</th><th class="col-optional">Harsh braking</th><th>Flags</th></tr></thead>
      <tbody>
        <tr v-for="p in pilots" :key="p.name" :class="p.rowClass">
          <td class="ico"><UserRound :size="14" class="muted" />{{ p.name }}</td>
          <td>
            <div class="pp-bar-wrap">
              <div class="pp-bar"><div class="pp-bar-fill" :class="p.rowClass" :style="{ width: p.score + '%' }"></div></div>
              <b>{{ p.score }}</b>
            </div>
          </td>
          <td class="col-optional">{{ p.overspeed }}</td>
          <td class="col-optional">{{ p.harshBraking }}</td>
          <td>
            <span v-if="!p.flags.length" class="muted">None</span>
            <span v-for="f in p.flags" :key="f" class="badge critical" style="margin-right:4px">{{ f }}</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Gauge, Zap, Flag, UserRound } from 'lucide-vue-next'
import { motion } from 'motion-v'
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

const avgScore = computed(() => pilots.reduce((s, p) => s + p.score, 0) / pilots.length)
const totalOverspeed = computed(() => pilots.reduce((s, p) => s + p.overspeed, 0))
const totalFlags = computed(() => pilots.reduce((s, p) => s + p.flags.length, 0))
</script>

<style scoped>
.pp-bar-wrap { display: flex; align-items: center; gap: 10px; }
.pp-bar { width: 90px; height: 7px; border-radius: 999px; background: var(--surface-2); overflow: hidden; flex: none; }
.pp-bar-fill { height: 100%; border-radius: 999px; background: var(--green); }
.pp-bar-fill.idle { background: var(--amber); }
.pp-bar-fill.critical { background: var(--crit); }

@media (max-width: 720px) {
  .col-optional { display: none; }
  table { min-width: 0; }
}
</style>
