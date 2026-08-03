<template>
  <div class="topbar">
    <h1>Order Booking</h1>
    <span class="muted">{{ orders.length }} order(s)</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-blue hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg blue ic"><ClipboardList :size="20" class="icon-lg" /></span><div class="n">{{ orders.length }}</div><div class="l">Total orders</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><Clock3 :size="20" class="icon-lg" /></span><div class="n">{{ counts.pending }}</div><div class="l">Pending</div>
    </motion.div>
    <motion.div class="card kpi glow-green" :while-hover="{ y: -2 }">
      <span class="icon-chip lg green ic"><CheckCircle2 :size="20" class="icon-lg" /></span><div class="n">{{ counts.fulfilled }}</div><div class="l">Fulfilled</div>
    </motion.div>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Order ID</th><th>Customer</th><th>Date</th><th>Status</th></tr></thead>
      <tbody>
        <tr v-for="o in orders" :key="o.id" :class="o.rowClass">
          <td style="font-weight:600">{{ o.orderId }}</td>
          <td>{{ o.customer }}</td>
          <td class="muted">{{ o.date }}</td>
          <td><span class="badge" :class="o.rowClass">{{ o.statusLabel }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ClipboardList, Clock3, CheckCircle2 } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_CUSTOMERS, seededRandom, pick, rangeInt, addDays, fmtDate } from '../mock'

const rng = seededRandom(1313)
const today = new Date()
const STATUS = [
  { label: 'Pending', cls: 'idle' },
  { label: 'Confirmed', cls: 'info' },
  { label: 'Fulfilled', cls: 'active' },
  { label: 'Cancelled', cls: 'offline' },
]

const orders = Array.from({ length: 22 }, (_, i) => {
  const st = pick(rng, [STATUS[0], STATUS[0], STATUS[1], STATUS[2], STATUS[2], STATUS[2], STATUS[3]])
  return {
    id: i + 1,
    orderId: `ORD-${String(5100 + i)}`,
    customer: pick(rng, MOCK_CUSTOMERS),
    date: fmtDate(addDays(today, -rangeInt(rng, 0, 30))),
    statusLabel: st.label,
    rowClass: st.cls,
  }
})

const counts = computed(() => ({
  pending: orders.filter((o) => o.statusLabel === 'Pending').length,
  fulfilled: orders.filter((o) => o.statusLabel === 'Fulfilled').length,
}))
</script>
