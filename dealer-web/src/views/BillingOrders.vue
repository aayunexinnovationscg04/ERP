<template>
  <PageHeader preview />

  <div class="kpis">
    <StatTile label="Total orders" :value="orders.length" :icon="ClipboardList" tone="blue" />
    <StatTile label="Pending" :value="counts.pending" :icon="Clock3" tone="amber" />
    <StatTile label="Fulfilled" :value="counts.fulfilled" :icon="CheckCircle2" tone="green" />
  </div>

  <div class="card flush">
    <div class="card-head">
      <label class="search">
        <Search :size="16" />
        <input v-model="q" type="search" placeholder="Search order or customer…" aria-label="Search orders" />
      </label>
    </div>
    <div class="table-wrap">
      <table class="mstack">
        <thead><tr><th>Order</th><th>Customer</th><th>Date</th><th class="hide-sm">Status</th></tr></thead>
        <tbody>
          <tr v-for="o in pager.rows.value" :key="o.id">
            <td class="cell-head cell-main nowrap">{{ o.orderId }}<span class="badge show-sm" :class="o.rowClass">{{ o.statusLabel }}</span></td>
            <td class="nowrap" data-label="Customer">{{ o.customer }}</td>
            <td class="muted nowrap" data-label="Date">{{ o.date }}</td>
            <td class="hide-sm"><span class="badge" :class="o.rowClass">{{ o.statusLabel }}</span></td>
          </tr>
          <tr v-if="!shown.length" class="table-empty"><td colspan="4" class="td-empty">No matching orders.</td></tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ClipboardList, Clock3, CheckCircle2, Search } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
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

const q = ref('')
const shown = computed(() => { const t = q.value.trim().toLowerCase(); return t ? orders.filter((o) => (o.orderId + ' ' + o.customer).toLowerCase().includes(t)) : orders })
const pager = usePaging(shown, 10, [q])
const counts = computed(() => ({
  pending: orders.filter((o) => o.statusLabel === 'Pending').length,
  fulfilled: orders.filter((o) => o.statusLabel === 'Fulfilled').length,
}))
</script>