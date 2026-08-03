<template>
  <div class="topbar">
    <h1>Challans &amp; Invoices</h1>
    <div class="row seg">
      <button :class="{ primary: tab === 'challans' }" @click="tab = 'challans'">Challans</button>
      <button :class="{ primary: tab === 'invoices' }" @click="tab = 'invoices'">Invoices</button>
    </div>
  </div>

  <div v-if="tab === 'challans'" class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Challan No.</th><th>Customer</th><th>Truck</th><th>Date</th><th>Status</th></tr></thead>
      <tbody>
        <tr v-for="c in challans" :key="c.id" :class="c.rowClass">
          <td style="font-weight:600">{{ c.no }}</td>
          <td>{{ c.customer }}</td>
          <td class="muted">{{ c.vehicle }}</td>
          <td class="muted">{{ c.date }}</td>
          <td><span class="badge" :class="c.rowClass">{{ c.statusLabel }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>

  <div v-else class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Invoice No.</th><th>Customer</th><th>Amount</th><th>Date</th><th>Status</th></tr></thead>
      <tbody>
        <tr v-for="inv in invoices" :key="inv.id" :class="inv.rowClass">
          <td style="font-weight:600">{{ inv.no }}</td>
          <td>{{ inv.customer }}</td>
          <td>₹{{ fmt(inv.amount, 0) }}</td>
          <td class="muted">{{ inv.date }}</td>
          <td><span class="badge" :class="inv.rowClass">{{ inv.statusLabel }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { MOCK_CUSTOMERS, MOCK_VEHICLES, seededRandom, pick, rangeInt, addDays, fmtDate } from '../mock'
import { fmt } from '../util'

const tab = ref('challans')
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
</script>

<style scoped>
.seg { background: var(--surface-2); border: 1px solid var(--border); padding: 3px; border-radius: var(--radius-pill); gap: 2px; }
.seg button { border: none; background: none; padding: 7px 16px; border-radius: var(--radius-pill); }
.seg button.primary { box-shadow: none; }
.seg button:not(.primary):hover { background: var(--surface-3); }
</style>
