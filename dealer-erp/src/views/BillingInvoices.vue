<template>
  <PageHeader title="Challans & Invoices" description="Delivery challans issued against trips and customer invoices with payment status." preview>
    <div class="seg" role="tablist" aria-label="Document type">
      <button role="tab" :aria-selected="tab === 'challans'" :class="{ on: tab === 'challans' }" @click="tab = 'challans'">Challans</button>
      <button role="tab" :aria-selected="tab === 'invoices'" :class="{ on: tab === 'invoices' }" @click="tab = 'invoices'">Invoices</button>
    </div>
  </PageHeader>

  <div class="kpis" v-if="tab === 'invoices'">
    <StatTile label="Invoiced" :value="'₹' + inr(invTotal)" :icon="Receipt" tone="navy" :sub="`${invoices.length} invoices`" />
    <StatTile label="Paid" :value="'₹' + inr(invPaid)" :icon="CheckCircle2" tone="green" />
    <StatTile label="Outstanding" :value="'₹' + inr(invTotal - invPaid)" :icon="Clock3" tone="crit" />
  </div>
  <div class="kpis" v-else>
    <StatTile label="Challans" :value="challans.length" :icon="FileText" tone="navy" />
    <StatTile label="Delivered" :value="challans.filter((c) => c.statusLabel === 'Delivered').length" :icon="CheckCircle2" tone="green" />
    <StatTile label="In transit" :value="challans.filter((c) => c.statusLabel === 'In transit').length" :icon="Truck" tone="amber" />
  </div>

  <div v-if="tab === 'challans'" class="card flush">
    <div class="table-wrap">
      <table>
        <thead><tr><th>Challan</th><th>Customer</th><th>Truck</th><th>Date</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="c in challans" :key="c.id">
            <td class="cell-main nowrap">{{ c.no }}</td>
            <td class="nowrap">{{ c.customer }}</td>
            <td class="nowrap muted">{{ c.vehicle }}</td>
            <td class="nowrap muted">{{ c.date }}</td>
            <td><span class="badge" :class="c.rowClass">{{ c.statusLabel }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div v-else class="card flush">
    <div class="table-wrap">
      <table>
        <thead><tr><th>Invoice</th><th>Customer</th><th class="num">Amount</th><th>Date</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="inv in invoices" :key="inv.id">
            <td class="cell-main nowrap">{{ inv.no }}</td>
            <td class="nowrap">{{ inv.customer }}</td>
            <td class="num cell-main">₹{{ inr(inv.amount) }}</td>
            <td class="nowrap muted">{{ inv.date }}</td>
            <td><span class="badge" :class="inv.rowClass">{{ inv.statusLabel }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Receipt, CheckCircle2, Clock3, FileText, Truck } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
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
const invTotal = invoices.reduce((a, i) => a + i.amount, 0)
const invPaid = invoices.filter((i) => i.statusLabel === 'Paid').reduce((a, i) => a + i.amount, 0)
</script>