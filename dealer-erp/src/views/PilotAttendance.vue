<template>
  <div class="topbar">
    <h1>Pilot Attendance</h1>
    <span class="muted">{{ monthLabel }}</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-green hero" :while-hover="{ y: -2 }">
      <span class="icon-chip lg green ic"><CalendarCheck :size="20" class="icon-lg" /></span><div class="n">{{ fmt(fleetAttendancePct, 0) }}%</div><div class="l">Fleet attendance</div>
    </motion.div>
    <motion.div class="card kpi glow-crit" :while-hover="{ y: -2 }">
      <span class="icon-chip lg crit ic"><CalendarX :size="20" class="icon-lg" /></span><div class="n">{{ totalAbsent }}</div><div class="l">Absences this month</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><CalendarClock :size="20" class="icon-lg" /></span><div class="n">{{ totalLeave }}</div><div class="l">Leave days</div>
    </motion.div>
  </div>

  <p class="section-title">Monthly Summary</p>
  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Pilot</th><th>Present</th><th>Absent</th><th>Leave</th><th>Attendance</th></tr></thead>
      <tbody>
        <tr v-for="p in summary" :key="p.name">
          <td class="ico"><UserRound :size="14" class="muted" />{{ p.name }}</td>
          <td>{{ p.present }} / {{ daysInMonth }}</td>
          <td>{{ p.absent }}</td>
          <td>{{ p.leave }}</td>
          <td>
            <span class="badge" :class="p.pct >= 90 ? 'active' : p.pct >= 75 ? 'idle' : 'critical'">{{ fmt(p.pct, 0) }}%</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <p class="section-title">Calendar View</p>
  <div class="card" style="padding:16px 18px">
    <div class="row" style="margin-bottom:14px">
      <span class="muted" style="font-size:13px">Pilot</span>
      <select v-model="selectedPilot" style="max-width:220px">
        <option v-for="p in summary" :key="p.name" :value="p.name">{{ p.name }}</option>
      </select>
    </div>
    <div class="pa-cal">
      <div class="pa-cal-dow muted" v-for="d in ['S','M','T','W','T','F','S']" :key="d">{{ d }}</div>
      <div class="pa-cal-pad" v-for="n in leadingBlanks" :key="'b'+n"></div>
      <div class="pa-cal-cell" v-for="day in selectedCalendar" :key="day.date" :class="day.status" :title="`${day.date}: ${day.label}`">
        {{ day.day }}
      </div>
    </div>
    <div class="row pa-legend">
      <span class="ico muted"><span class="dot green"></span> Present</span>
      <span class="ico muted"><span class="dot red"></span> Absent</span>
      <span class="ico muted"><span class="dot gray"></span> Leave</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { CalendarCheck, CalendarX, CalendarClock, UserRound } from 'lucide-vue-next'
import { motion } from 'motion-v'
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

const selectedPilot = ref(MOCK_PILOTS[0])
const selectedCalendar = computed(() => perPilot.find((p) => p.name === selectedPilot.value)?.days || [])
</script>

<style scoped>
.pa-cal { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
.pa-cal-dow { text-align: center; font-size: 11px; font-weight: 700; text-transform: uppercase; padding-bottom: 4px; }
.pa-cal-pad { }
.pa-cal-cell {
  aspect-ratio: 1; display: grid; place-items: center; border-radius: 8px; font-size: 12.5px; font-weight: 600;
  background: var(--surface-2); color: var(--muted);
}
.pa-cal-cell.present { background: var(--green-soft); color: var(--green); }
.pa-cal-cell.absent { background: var(--crit-soft); color: var(--crit); }
.pa-cal-cell.leave { background: var(--gray-soft); color: var(--gray); }
.pa-legend { gap: 16px; margin-top: 14px; font-size: 12.5px; flex-wrap: wrap; }
</style>
