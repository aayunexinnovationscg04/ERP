<template>
  <PageHeader preview />

  <div class="kpis">
    <StatTile label="Fleet attendance" :value="fmt(fleetAttendancePct, 0)" unit="%" :icon="CalendarCheck" tone="green" />
    <StatTile label="Absences" :value="totalAbsent" :icon="CalendarX" tone="crit" />
    <StatTile label="Leave days" :value="totalLeave" :icon="CalendarClock" tone="amber" />
  </div>

  <div class="grid-2">
    <div class="card flush">
      <div class="card-head"><div class="card-head-title"><Users :size="17" /><h2>{{ monthLabel }}</h2></div></div>
      <div class="table-wrap">
        <table class="mstack">
          <thead><tr><th>Pilot</th><th class="num">Present</th><th class="num">Absent</th><th class="num">Leave</th><th>Attendance</th></tr></thead>
          <tbody>
            <tr v-for="p in pager.rows.value" :key="p.name" class="clickable" :class="{ sel: p.name === selectedPilot }" @click="selectedPilot = p.name">
              <td class="cell-head cell-main nowrap">{{ p.name }}<span class="badge show-sm" :class="p.pct >= 90 ? 'active' : p.pct >= 75 ? 'idle' : 'critical'">{{ fmt(p.pct, 0) }}%</span></td>
              <td class="num" data-label="Present">{{ p.present }}</td>
              <td class="num" data-label="Absent">{{ p.absent }}</td>
              <td class="num" data-label="Leave">{{ p.leave }}</td>
              <td class="hide-sm"><span class="badge" :class="p.pct >= 90 ? 'active' : p.pct >= 75 ? 'idle' : 'critical'">{{ fmt(p.pct, 0) }}%</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <Pager :pager="pager" />
    </div>

    <div class="card">
      <div class="card-head">
        <div class="card-head-title"><CalendarDays :size="17" /><h2>Calendar</h2></div>
        <select v-model="selectedPilot" class="pa-select" aria-label="Pilot">
          <option v-for="p in summary" :key="p.name" :value="p.name">{{ p.name }}</option>
        </select>
      </div>
      <div class="card-body">
        <div class="pa-cal">
          <div class="pa-cal-dow" v-for="(d, i) in ['S','M','T','W','T','F','S']" :key="i">{{ d }}</div>
          <div v-for="n in leadingBlanks" :key="'b'+n"></div>
          <div class="pa-cal-cell" v-for="day in selectedCalendar" :key="day.date" :class="day.status" :title="`${day.date}: ${day.label}`">
            {{ day.day }}
          </div>
        </div>
        <div class="map-legend" style="margin-top:14px">
          <span><i class="swatch" style="background:var(--green)"></i>Present</span>
          <span><i class="swatch" style="background:var(--crit)"></i>Absent</span>
          <span><i class="swatch" style="background:var(--muted-2)"></i>Leave</span>
          <span><i class="swatch" style="background:var(--surface-3);border:1px solid var(--border-strong)"></i>Upcoming</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { CalendarCheck, CalendarX, CalendarClock, CalendarDays, Users } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { MOCK_PILOTS, seededRandom, pick } from '../mock'
import { fmt } from '../util'

const today = new Date()
const year = today.getFullYear()
const month = today.getMonth()
const daysInMonth = new Date(year, month + 1, 0).getDate()
const monthLabel = today.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })
const leadingBlanks = new Date(year, month, 1).getDay()

const rng = seededRandom(808)
const STATUS_LABEL = { present: 'Present', absent: 'Absent', leave: 'Leave' }

const perPilot = MOCK_PILOTS.map((name) => {
  const days = []
  for (let d = 1; d <= daysInMonth; d++) {
    const isFuture = new Date(year, month, d) > today
    const status = isFuture ? null : pick(rng, ['present', 'present', 'present', 'present', 'present', 'present', 'absent', 'leave'])
    days.push({ day: d, date: `${d} ${monthLabel}`, status, label: status ? STATUS_LABEL[status] : 'Upcoming' })
  }
  const present = days.filter((d) => d.status === 'present').length
  const absent = days.filter((d) => d.status === 'absent').length
  const leave = days.filter((d) => d.status === 'leave').length
  const counted = present + absent + leave
  return { name, days, present, absent, leave, pct: counted ? (present / counted) * 100 : 100 }
})

const summary = perPilot
const totalAbsent = computed(() => summary.reduce((s, p) => s + p.absent, 0))
const totalLeave = computed(() => summary.reduce((s, p) => s + p.leave, 0))
const fleetAttendancePct = computed(() => summary.reduce((s, p) => s + p.pct, 0) / summary.length)

const pager = usePaging(computed(() => summary), 10)
const selectedPilot = ref(MOCK_PILOTS[0])
const selectedCalendar = computed(() => perPilot.find((p) => p.name === selectedPilot.value)?.days || [])
</script>
<style scoped>
.pa-select { width: auto; min-width: 170px; }
tr.sel td { background: var(--brand-soft); }
tr.sel { background: var(--brand-soft); }
@media (max-width: 720px) {
  table.mstack tbody tr { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .pa-select { min-width: 0; flex: 1 1 160px; }
  .pa-cal { gap: 4px; }
}
.pa-cal { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 6px; }
.pa-cal-dow { text-align: center; font-size: 11px; font-weight: 700; color: var(--muted); padding-bottom: 2px; }
.pa-cal-cell {
  aspect-ratio: 1; display: grid; place-items: center; border-radius: 6px; font-size: 12.5px; font-weight: 700;
  background: var(--surface-2); color: var(--muted-2); border: 1px solid var(--border);
}
.pa-cal-cell.present { background: var(--green-soft); color: var(--green); border-color: transparent; }
.pa-cal-cell.absent { background: var(--crit-soft); color: var(--crit); border-color: transparent; }
.pa-cal-cell.leave { background: var(--surface-3); color: var(--muted); border-color: transparent; }
</style>
