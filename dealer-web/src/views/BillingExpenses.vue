<template>
  <PageHeader preview />

  <div class="kpis">
    <StatTile label="Month total" :value="'₹' + inr(total)" :icon="Wallet" tone="navy" />
    <StatTile v-for="c in byCategory.slice(0, 3)" :key="c.name" :label="c.short || c.name" :value="'₹' + inr(c.total)" :icon="c.icon" :tone="c.hue" />
  </div>

  <div class="grid-2">
    <div class="card flush">
      <div class="card-head"><div class="card-head-title"><ReceiptText :size="17" /><h2>Recent expenses</h2></div></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Expense</th><th class="hide-sm">Date</th><th class="num">Amount</th></tr></thead>
          <tbody>
            <tr v-for="e in pager.rows.value" :key="e.id">
              <td><div class="cell-with-icon"><span class="icon-chip sm gray"><component :is="e.icon" :size="13" /></span>
                <div style="min-width:0"><div class="cell-main" style="font-weight:600">{{ e.desc }}</div><div class="cell-sub">{{ e.category }}<span class="show-sm"> · {{ e.date }}</span></div></div></div></td>
              <td class="muted nowrap hide-sm">{{ e.date }}</td>
              <td class="num cell-main">₹{{ inr(e.amount) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <Pager :pager="pager" />
    </div>

    <div class="card">
      <div class="card-head"><div class="card-head-title"><PieChart :size="17" /><h2>Spend by category</h2></div></div>
      <div class="card-body be-cats">
        <div class="be-cat" v-for="c in byCategory" :key="c.name">
          <div class="be-cat-top">
            <span class="ico"><span class="icon-chip sm" :class="c.hue"><component :is="c.icon" :size="13" /></span>{{ c.name }}</span>
            <b class="num">₹{{ inr(c.total) }}</b>
          </div>
          <div class="meter"><span :class="barClass[c.hue]" :style="{ width: (c.total / maxCat * 100) + '%' }"></span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Wallet, Fuel, Wrench, IdCard, ShieldCheck, MoreHorizontal, ReceiptText, PieChart } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { MOCK_VEHICLES, seededRandom, pick, rangeInt, addDays, fmtDate } from '../mock'

const inr = (n) => Math.round(n).toLocaleString('en-IN')
const barClass = { brand: 'brand', amber: 'amber', teal: 'green', blue: '', gray: 'gray' }
const monthLabel = new Date().toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })
const today = new Date()
const rng = seededRandom(1515)

const CATEGORIES = [
  { name: 'Fuel', icon: Fuel, hue: 'brand' },
  { name: 'Maintenance', icon: Wrench, hue: 'amber' },
  { name: 'Pilot wages', icon: IdCard, hue: 'teal' },
  { name: 'Insurance & compliance', short: 'Insurance', icon: ShieldCheck, hue: 'blue' },
  { name: 'Miscellaneous', short: 'Misc.', icon: MoreHorizontal, hue: 'gray' },
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

const pager = usePaging(computed(() => expenses), 10)
const byCategory = computed(() => CATEGORIES.map((c) => ({
  ...c, total: expenses.filter((e) => e.category === c.name).reduce((s, e) => s + e.amount, 0),
})).sort((a, b) => b.total - a.total))
const maxCat = computed(() => Math.max(...byCategory.value.map((c) => c.total), 1))
const total = computed(() => expenses.reduce((s, e) => s + e.amount, 0))
</script>
<style scoped>
.be-cats { display: flex; flex-direction: column; gap: 16px; }
.be-cat-top { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 13.5px; font-weight: 600; }
.be-cat-top b { color: var(--ink-strong); }
.be-cat .meter { height: 8px; }
</style>
