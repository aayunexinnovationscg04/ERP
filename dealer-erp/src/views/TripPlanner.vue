<template>
  <div class="topbar">
    <h1>Trip Planner</h1>
    <span class="muted">{{ trips.length }} scheduled trip(s)</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-blue" :while-hover="{ y: -2 }">
      <span class="icon-chip lg blue ic"><CalendarClock :size="20" class="icon-lg" /></span><div class="n">{{ counts.scheduled }}</div><div class="l">Scheduled</div>
    </motion.div>
    <motion.div class="card kpi glow-amber hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><Navigation :size="20" class="icon-lg" /></span><div class="n">{{ counts.inProgress }}</div><div class="l">In progress</div>
    </motion.div>
    <motion.div class="card kpi glow-green" :while-hover="{ y: -2 }">
      <span class="icon-chip lg green ic"><CheckCircle2 :size="20" class="icon-lg" /></span><div class="n">{{ counts.completed }}</div><div class="l">Completed</div>
    </motion.div>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Trip</th><th>Truck</th><th>Pilot</th><th>Scheduled</th><th>Status</th></tr></thead>
      <tbody>
        <tr v-for="t in trips" :key="t.id" :class="t.rowClass">
          <td style="font-weight:600">{{ t.tripId }}</td>
          <td>{{ t.vehicleName }}</td>
          <td class="ico"><UserRound :size="13" class="muted" />{{ t.pilotName }}</td>
          <td class="muted">{{ t.scheduled }}</td>
          <td><span class="badge" :class="t.rowClass">{{ t.statusLabel }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CalendarClock, Navigation, CheckCircle2, UserRound } from 'lucide-vue-next'
import { motion } from 'motion-v'
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

const counts = computed(() => ({
  scheduled: trips.filter((t) => t.statusLabel === 'Scheduled').length,
  inProgress: trips.filter((t) => t.statusLabel === 'In progress').length,
  completed: trips.filter((t) => t.statusLabel === 'Completed').length,
}))
</script>
