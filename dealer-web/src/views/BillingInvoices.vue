<template>
  <PageHeader preview />

  <div class="kpis" v-if="tab === 'invoices'">
    <StatTile label="Invoiced" :value="'₹' + inr(invTotal)" :icon="Receipt" tone="navy" />
    <StatTile label="Paid" :value="'₹' + inr(invPaid)" :icon="CheckCircle2" tone="green" />
    <StatTile label="Outstanding" :value="'₹' + inr(invTotal - invPaid)" :icon="Clock3" tone="crit" />
  </div>
  <div class="kpis" v-else>
    <StatTile label="Challans" :value="challans.length" :icon="FileText" tone="navy" />
    <StatTile label="Delivered" :value="challans.filter((c) => c.statusLabel === 'Delivered').length" :icon="CheckCircle2" tone="green" />
    <StatTile label="In transit" :value="challans.filter((c) => c.statusLabel === 'In transit').length" :icon="Truck" tone="amber" />
  </div>

  <div class="card flush">
    <div class="card-head">
      <div class="seg" role="tablist" aria-label="Document type">
        <button role="tab" :aria-selected="tab === 'challans'" :class="{ on: tab === 'challans' }" @click="tab = 'challans'">Challans <span class="muted">{{ challans.length }}</span></button>
        <button role="tab" :aria-selected="tab === 'invoices'" :class="{ on: tab === 'invoices' }" @click="tab = 'invoices'">Invoices <span class="muted">{{ invoices.length }}</span></button>
      </div>
    </div>
    <template v-if="tab === 'challans'">
      <div class="table-wrap">
        <table class="mstack">
          <thead><tr><th>Challan</th><th>Customer</th><th>Truck</th><th>Date</th><th class="hide-sm">Status</th></tr></thead>
          <tbody>
            <tr v-for="c in chPager.rows.value" :key="c.id">
              <td class="cell-head cell-main nowrap">{{ c.no }}<span class="badge show-sm" :class="c.rowClass">{{ c.statusLabel }}</span></td>
              <td class="nowrap" data-label="Customer">{{ c.customer }}</td>
              <td class="nowrap muted" data-label="Truck">{{ c.vehicle }}</td>
              <td class="nowrap muted" data-label="Date">{{ c.date }}</td>
              <td class="hide-sm"><span class="badge" :class="c.rowClass">{{ c.statusLabel }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <Pager :pager="chPager" />
    </template>

    <template v-else>
      <div class="table-wrap">
        <table class="mstack">
          <thead><tr><th>Invoice</th><th>Customer</th><th class="num">Amount</th><th>Date</th><th class="hide-sm">Status</th></tr></thead>
          <tbody>
            <tr v-for="inv in invPager.rows.value" :key="inv.id">
              <td class="cell-head cell-main nowrap">{{ inv.no }}<span class="badge show-sm" :class="inv.rowClass">{{ inv.statusLabel }}</span></td>
              <td class="nowrap" data-label="Customer">{{ inv.customer }}</td>
              <td class="num cell-main" data-label="Amount">₹{{ inr(inv.amount) }}</td>
              <td class="nowrap muted" data-label="Date">{{ inv.date }}</td>
              <td class="hide-sm"><span class="badge" :class="inv.rowClass">{{ inv.statusLabel }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <Pager :pager="invPager" />
    </template>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { Receipt, CheckCircle2, Clock3, FileText, Truck } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { MOCK_CUSTOMERS, MOCK_VEHICLES, seededRandom, pick, rangeInt, addDays, fmtDate } from '../mock'

const tab = ref('challans')
const inr = (n) => Math.round(n).toLocaleString('en-IN')
const rng = seededRandom(1414)
const today = new Date()

const CHALLAN_STATUS = [{ label: 'Delivered', cls: 'active' }, { label: 'In transit', cls: 'idle' }, { label: 'Pending', cls: 'offline' }]
const INVOICE_STATUS = [{ label: 'Paid', cls: 'active' }, { label: 'Unpaid', cls: 'critical' }, { label: 'Overdue', cls: 'critical' }]

const challans = Array.from({ length: 14 }, (_, i) => {
  const st = pick(rng, CHALLAN_STATUS)
  return {
    id: i + 1, no: `CHL-${String(9000 + i)}`,
    customer: pick(rng, MOCK_CUSTOMERS), vehicle: pick(rng, MOCK_VEHICLES).name,
    date: fmtDate(addDays(today, -rangeInt(rng, 0, 25))),
    statusLabel: st.label, rowClass: st.cls,
  }
})

const invoices = Array.from({ length: 14 }, (_, i) => {
  const st = pick(rng, INVOICE_STATUS)
  return {
    id: i + 1, no: `INV-${String(7700 + i)}`,
    customer: pick(rng, MOCK_CUSTOMERS), amount: rangeInt(rng, 8000, 95000),
    date: fmtDate(addDays(today, -rangeInt(rng, 0, 40))),
    statusLabel: st.label, rowClass: st.cls,
  }
})
const chPager = usePaging(computed(() => challans), 10)
const invPager = usePaging(computed(() => invoices), 10)
const invTotal = invoices.reduce((a, i) => a + i.amount, 0)
const invPaid = invoices.filter((i) => i.statusLabel === 'Paid').reduce((a, i) => a + i.amount, 0)
</script>

<style scoped>
.seg .muted { font-size: 11.5px; font-weight: 700; }
@media (max-width: 720px) {
  table.mstack tbody tr { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .card-head .seg { flex: 1 1 100%; }
  .card-head .seg button { flex: 1; }
}
</style>
