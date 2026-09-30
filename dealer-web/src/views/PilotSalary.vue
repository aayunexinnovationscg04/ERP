<template>
  <PageHeader title="Salary" :description="`Pilot pay for ${monthLabel}: base, bonuses, deductions and net payout.`" preview />

  <div class="kpis">
    <StatTile label="Total payout" :value="'₹' + inr(totalPayout)" :icon="Wallet" tone="navy" />
    <StatTile label="Bonuses" :value="'₹' + inr(totalBonus)" :icon="TrendingUp" tone="green" />
    <StatTile label="Deductions" :value="'₹' + inr(totalDeductions)" :icon="TrendingDown" tone="amber" />
  </div>

  <div class="card flush">
    <div class="card-head"><div class="card-head-title"><Users :size="17" /><h2>{{ monthLabel }}</h2></div></div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Pilot</th><th class="num">Base pay</th><th class="num">Bonus</th><th class="num">Deductions</th><th class="num">Net pay</th></tr></thead>
        <tbody>
          <tr v-for="s in salaries" :key="s.name">
            <td class="cell-main nowrap">{{ s.name }}</td>
            <td class="num">₹{{ inr(s.base) }}</td>
            <td class="num" style="color:var(--green)">+₹{{ inr(s.bonus) }}</td>
            <td class="num" style="color:var(--crit)">−₹{{ inr(s.deductions) }}</td>
            <td class="num cell-main">₹{{ inr(s.net) }}</td>
          </tr>
        </tbody>
        <tfoot>
          <tr><td class="cell-main">Total</td><td class="num">₹{{ inr(salaries.reduce((a, s) => a + s.base, 0)) }}</td>
            <td class="num">+₹{{ inr(totalBonus) }}</td><td class="num">−₹{{ inr(totalDeductions) }}</td><td class="num cell-main">₹{{ inr(totalPayout) }}</td></tr>
        </tfoot>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Wallet, TrendingUp, TrendingDown, Users } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import { MOCK_PILOTS, seededRandom, rangeInt } from '../mock'

const inr = (n) => Math.round(n).toLocaleString('en-IN')
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
<style scoped>
tfoot td { background: var(--surface-2); border-top: 1px solid var(--border-strong); border-bottom: none; font-weight: 700; }
</style>
