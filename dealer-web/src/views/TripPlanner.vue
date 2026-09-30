<template>
  <PageHeader preview />

  <div class="kpis">
    <StatTile label="Scheduled" :value="counts.scheduled" :icon="CalendarClock" tone="blue" />
    <StatTile label="In progress" :value="counts.inProgress" :icon="Navigation" tone="amber" />
    <StatTile label="Completed" :value="counts.completed" :icon="CheckCircle2" tone="green" />
  </div>

  <div class="card flush">
    <div class="card-head">
      <div class="card-head-title"><RouteIcon :size="17" /><h2>Trips</h2></div>
      <div class="seg" role="group" aria-label="Filter trips">
        <button v-for="f in FILTERS" :key="f.key" :class="{ on: filter === f.key }" @click="filter = f.key">{{ f.label }}</button>
      </div>
    </div>
    <div class="table-wrap">
      <table class="mstack">
        <thead><tr><th>Trip</th><th>Truck</th><th>Pilot</th><th>Date</th><th class="hide-sm">Status</th></tr></thead>
        <tbody>
          <tr v-for="t in pager.rows.value" :key="t.id">
            <td class="cell-head cell-main nowrap">{{ t.tripId }}<span class="badge show-sm" :class="t.rowClass">{{ t.statusLabel }}</span></td>
            <td class="nowrap" data-label="Truck">{{ t.vehicleName }}</td>
            <td class="nowrap" data-label="Pilot">{{ t.pilotName }}</td>
            <td class="nowrap muted" data-label="Date">{{ t.scheduled }}</td>
            <td class="hide-sm"><span class="badge" :class="t.rowClass">{{ t.statusLabel }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { CalendarClock, Navigation, CheckCircle2, Route as RouteIcon } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { MOCK_VEHICLES, MOCK_PILOTS, seededRandom, pick, rangeInt, addDays, fmtDate } from '../mock'

const rng = seededRandom(1111)
const today = new Date()
const STATUS = [
  { key: 'scheduled', label: 'Scheduled', cls: 'info' },
  { key: 'inProgress', label: 'In progress', cls: 'idle' },
  { key: 'completed', label: 'Completed', cls: 'active' },
]

const trips = Array.from({ length: 16 }, (_, i) => {
  const v = pick(rng, MOCK_VEHICLES)
  const pilot = pick(rng, MOCK_PILOTS)
  const offset = rangeInt(rng, -6, 10)
  const st = offset < 0 ? STATUS[2] : offset === 0 ? STATUS[1] : STATUS[0]
  return {
    id: i + 1,
    tripId: `TRP-${String(2400 + i).padStart(4, '0')}`,
    vehicleName: v.name,
    pilotName: pilot,
    scheduled: fmtDate(addDays(today, offset)),
    statusLabel: st.label,
    rowClass: st.cls,
    sortKey: offset,
  }
}).sort((a, b) => a.sortKey - b.sortKey)

const FILTERS = [{ key: '', label: 'All' }, { key: 'Scheduled', label: 'Upcoming' }, { key: 'In progress', label: 'Live' }, { key: 'Completed', label: 'Done' }]
const filter = ref('')
const shown = computed(() => (filter.value ? trips.filter((t) => t.statusLabel === filter.value) : trips))
const pager = usePaging(shown, 10, [filter])
const counts = computed(() => ({
  scheduled: trips.filter((t) => t.statusLabel === 'Scheduled').length,
  inProgress: trips.filter((t) => t.statusLabel === 'In progress').length,
  completed: trips.filter((t) => t.statusLabel === 'Completed').length,
}))
</script>

<style scoped>
@media (max-width: 720px) {
  table.mstack tbody tr { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .card-head .seg { flex: 1 1 100%; }
  .card-head .seg button { flex: 1; }
}
</style>