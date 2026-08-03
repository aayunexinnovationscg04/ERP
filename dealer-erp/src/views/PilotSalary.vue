<template>
  <div class="topbar">
    <h1>Pilot Salary</h1>
    <span class="muted">{{ monthLabel }}</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-violet hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg violet ic"><Wallet :size="20" class="icon-lg" /></span><div class="n">₹{{ fmt(totalPayout, 0) }}</div><div class="l">Total payout</div>
    </motion.div>
    <motion.div class="card kpi glow-green" :while-hover="{ y: -2 }">
      <span class="icon-chip lg green ic"><TrendingUp :size="20" class="icon-lg" /></span><div class="n">₹{{ fmt(totalBonus, 0) }}</div><div class="l">Total bonuses</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><TrendingDown :size="20" class="icon-lg" /></span><div class="n">₹{{ fmt(totalDeductions, 0) }}</div><div class="l">Total deductions</div>
    </motion.div>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Pilot</th><th>Month</th><th>Base pay</th><th>Bonus</th><th>Deductions</th><th>Net pay</th></tr></thead>
      <tbody>
        <tr v-for="s in salaries" :key="s.name">
          <td class="ico"><UserRound :size="14" class="muted" />{{ s.name }}</td>
          <td class="muted">{{ monthLabel }}</td>
          <td>₹{{ fmt(s.base, 0) }}</td>
          <td class="ico" style="color:var(--green)"><Plus :size="12" />₹{{ fmt(s.bonus, 0) }}</td>
          <td class="ico" style="color:var(--crit)"><Minus :size="12" />₹{{ fmt(s.deductions, 0) }}</td>
          <td><b>₹{{ fmt(s.net, 0) }}</b></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Wallet, TrendingUp, TrendingDown, UserRound, Plus, Minus } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_PILOTS, seededRandom, rangeInt } from '../mock'
import { fmt } from '../util'

const monthLabel = new Date().toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })
const rng = seededRandom(1010)

const salaries = MOCK_PILOTS.map((name) => {
  const base = rangeInt(rng, 16000, 24000)
  const bonus = rangeInt(rng, 0, 2500)
  const deductions = rangeInt(rng, 0, 1800)
  return { name, base, bonus, deductions, net: base + bonus - deductions }
})

const totalPayout = computed(() => salaries.reduce((s, r) => s + r.net, 0))
const totalBonus = computed(() => salaries.reduce((s, r) => s + r.bonus, 0))
const totalDeductions = computed(() => salaries.reduce((s, r) => s + r.deductions, 0))
</script>
