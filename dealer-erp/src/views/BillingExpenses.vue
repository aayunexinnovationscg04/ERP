<template>
  <div class="topbar">
    <h1>Expense Tracking</h1>
    <span class="muted">{{ monthLabel }}</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-crit hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg crit ic"><Wallet :size="20" class="icon-lg" /></span><div class="n">₹{{ fmt(total, 0) }}</div><div class="l">Total this month</div>
    </motion.div>
    <motion.div class="card kpi glow-violet" v-for="c in byCategory.slice(0, 3)" :key="c.name" :while-hover="{ y: -2 }">
      <span class="icon-chip lg violet ic"><component :is="c.icon" :size="20" class="icon-lg" /></span><div class="n">₹{{ fmt(c.total, 0) }}</div><div class="l">{{ c.name }}</div>
    </motion.div>
  </div>

  <p class="section-title">Spend by Category</p>
  <div class="card" style="padding:18px 20px">
    <div class="be-cat-row" v-for="c in byCategory" :key="c.name">
      <span class="icon-chip" :class="c.hue"><component :is="c.icon" :size="15" /></span>
      <span class="be-cat-name">{{ c.name }}</span>
      <div class="be-cat-bar"><div class="be-cat-fill" :class="c.hue" :style="{ width: (c.total / maxCat * 100) + '%' }"></div></div>
      <b class="be-cat-val">₹{{ fmt(c.total, 0) }}</b>
    </div>
  </div>

  <p class="section-title">Recent Expenses</p>
  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Date</th><th>Category</th><th>Description</th><th>Amount</th></tr></thead>
      <tbody>
        <tr v-for="e in expenses" :key="e.id">
          <td class="muted">{{ e.date }}</td>
          <td class="ico"><component :is="e.icon" :size="14" class="muted" />{{ e.category }}</td>
          <td class="muted">{{ e.desc }}</td>
          <td>₹{{ fmt(e.amount, 0) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Wallet, Fuel, Wrench, IdCard, ShieldCheck, MoreHorizontal } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_VEHICLES, seededRandom, pick, rangeInt, addDays, fmtDate } from '../mock'
import { fmt } from '../util'

const monthLabel = new Date().toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })
const today = new Date()
const rng = seededRandom(1515)

const CATEGORIES = [
  { name: 'Fuel', icon: Fuel, hue: 'violet' },
  { name: 'Maintenance', icon: Wrench, hue: 'amber' },
  { name: 'Pilot wages', icon: IdCard, hue: 'teal' },
  { name: 'Insurance & compliance', icon: ShieldCheck, hue: 'blue' },
  { name: 'Miscellaneous', icon: MoreHorizontal, hue: 'gray' },
]
const DESCS = {
  Fuel: ['Diesel refill', 'Fuel top-up'],
  Maintenance: ['Tyre replacement', 'Engine service', 'Brake pad change'],
  'Pilot wages': ['Advance payment', 'Overtime pay'],
  'Insurance & compliance': ['Insurance premium', 'Permit renewal fee'],
  Miscellaneous: ['Toll charges', 'Parking fee', 'Cleaning'],
}

const expenses = Array.from({ length: 20 }, (_, i) => {
  const cat = pick(rng, CATEGORIES)
  return {
    id: i + 1, category: cat.name, icon: cat.icon,
    desc: `${pick(rng, DESCS[cat.name])} · ${pick(rng, MOCK_VEHICLES).name}`,
    amount: rangeInt(rng, 400, 12000),
    date: fmtDate(addDays(today, -rangeInt(rng, 0, 28))),
    sortKey: rangeInt(rng, 0, 28),
  }
}).sort((a, b) => a.sortKey - b.sortKey)

const byCategory = computed(() => CATEGORIES.map((c) => ({
  ...c, total: expenses.filter((e) => e.category === c.name).reduce((s, e) => s + e.amount, 0),
})).sort((a, b) => b.total - a.total))
const maxCat = computed(() => Math.max(...byCategory.value.map((c) => c.total), 1))
const total = computed(() => expenses.reduce((s, e) => s + e.amount, 0))
</script>

<style scoped>
.be-cat-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
.be-cat-name { width: 170px; flex: none; font-weight: 600; font-size: 13.5px; }
.be-cat-bar { flex: 1; height: 8px; border-radius: 999px; background: var(--surface-2); overflow: hidden; }
.be-cat-fill { height: 100%; border-radius: 999px; }
.be-cat-fill.violet { background: var(--violet); }
.be-cat-fill.amber { background: var(--amber); }
.be-cat-fill.teal { background: var(--teal); }
.be-cat-fill.blue { background: var(--blue); }
.be-cat-fill.gray { background: var(--gray); }
.be-cat-val { width: 100px; flex: none; text-align: right; }
</style>
