<template>
  <h1>My Profile</h1>
  <div class="muted" style="margin-bottom:14px">{{ auth.user?.username || 'Pilot' }} — attendance, performance, salary &amp; tasks</div>

  <div class="ptabs">
    <button v-for="t in TABS" :key="t.key" class="ptab" :class="{ active: activeTab === t.key }" @click="activeTab = t.key">
      <component :is="t.icon" :size="16" :stroke-width="2.25" />
      {{ t.label }}
    </button>
  </div>

  <AnimatePresence mode="wait">
    <!-- ---- Attendance ---- -->
    <motion.div v-if="activeTab === 'attendance'" key="attendance"
      :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }" :transition="pageTransition(reduced)">
      <div class="chips" style="margin-bottom:16px">
        <div class="chip">
          <span class="chip-ic emerald"><CalendarCheck :size="17" :stroke-width="2.25" /></span>
          <div class="chip-body"><div class="l">Present</div><div class="v">{{ attendanceCounts.present }} <small class="muted">days</small></div></div>
        </div>
        <div class="chip">
          <span class="chip-ic amber"><CalendarX :size="17" :stroke-width="2.25" /></span>
          <div class="chip-body"><div class="l">Leave</div><div class="v">{{ attendanceCounts.leave }} <small class="muted">days</small></div></div>
        </div>
        <div class="chip">
          <span class="chip-ic" style="background:var(--crit-soft); color:var(--crit-strong)"><CalendarX :size="17" :stroke-width="2.25" /></span>
          <div class="chip-body"><div class="l">Absent</div><div class="v">{{ attendanceCounts.absent }} <small class="muted">days</small></div></div>
        </div>
        <div class="chip">
          <span class="chip-ic cyan"><Calendar :size="17" :stroke-width="2.25" /></span>
          <div class="chip-body"><div class="l">This month</div><div class="v" style="font-size:16px">{{ monthLabel }}</div></div>
        </div>
      </div>

      <div class="section-title">Calendar</div>
      <div class="card" style="padding:16px">
        <div class="cal-grid cal-dow">
          <span v-for="d in ['S','M','T','W','T','F','S']" :key="d">{{ d }}</span>
        </div>
        <div class="cal-grid">
          <span v-for="n in leadingBlanks" :key="'b'+n" class="cal-cell blank"></span>
          <span v-for="d in attendanceDays" :key="d.day" class="cal-cell" :class="'st-' + d.status" :title="d.status">{{ d.day }}</span>
        </div>
        <div class="cal-legend">
          <span><i class="dot st-present"></i>Present</span>
          <span><i class="dot st-leave"></i>Leave</span>
          <span><i class="dot st-absent"></i>Absent</span>
          <span><i class="dot st-off"></i>Weekly off</span>
          <span><i class="dot st-upcoming"></i>Upcoming</span>
        </div>
      </div>
    </motion.div>

    <!-- ---- Performance ---- -->
    <motion.div v-else-if="activeTab === 'performance'" key="performance"
      :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }" :transition="pageTransition(reduced)">
      <div class="card hero" style="margin-bottom:16px">
        <div class="row">
          <div>
            <div class="reg">{{ performance.score }}<small class="muted" style="font-size:16px">/100</small></div>
            <div class="sub">Overall driving score</div>
          </div>
          <div class="spacer"></div>
          <span class="badge" :class="performance.score >= 80 ? 'active' : performance.score >= 60 ? 'warning' : 'critical'">
            <span class="dot"></span>{{ performance.score >= 80 ? 'Excellent' : performance.score >= 60 ? 'Needs attention' : 'At risk' }}
          </span>
        </div>
        <div class="chips">
          <div class="chip">
            <span class="chip-ic amber"><Gauge :size="17" :stroke-width="2.25" /></span>
            <div class="chip-body"><div class="l">Overspeed violations</div><div class="v">{{ performance.overspeedCount }} <small class="muted">this month</small></div></div>
          </div>
          <div class="chip">
            <span class="chip-ic emerald"><TrendingUp :size="17" :stroke-width="2.25" /></span>
            <div class="chip-body"><div class="l">Trend</div><div class="v" style="font-size:16px">{{ performance.trend }}</div></div>
          </div>
        </div>
      </div>

      <div class="section-title">Behavior flags</div>
      <div v-for="(f, i) in performance.flags" :key="i" class="card item" :class="'sev-' + f.severity">
        <div class="item-row">
          <span class="item-ic" :class="f.severity === 'critical' ? 'critical' : f.severity === 'warning' ? 'warning' : 'on'">
            <component :is="f.icon" :size="17" :stroke-width="2.25" />
          </span>
          <div>
            <div class="t">{{ f.label }}</div>
            <div class="d">{{ f.detail }}</div>
          </div>
        </div>
        <span class="badge" :class="f.severity === 'critical' ? 'critical' : f.severity === 'warning' ? 'warning' : 'active'">{{ f.count }}</span>
      </div>
    </motion.div>

    <!-- ---- Salary ---- -->
    <motion.div v-else-if="activeTab === 'salary'" key="salary"
      :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }" :transition="pageTransition(reduced)">
      <div class="section-title">Pay history</div>
      <div class="card" style="padding:4px; overflow-x:auto">
        <table class="pay-table">
          <thead>
            <tr><th>Month</th><th>Base pay</th><th>Bonus / deductions</th><th>Net pay</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in salary" :key="row.month">
              <td class="muted">{{ row.month }}</td>
              <td>₹{{ row.base.toLocaleString('en-IN') }}</td>
              <td :style="{ color: row.adj >= 0 ? 'var(--green-strong)' : 'var(--red)' }">
                {{ row.adj >= 0 ? '+' : '' }}₹{{ row.adj.toLocaleString('en-IN') }}
              </td>
              <td class="t-numeral" style="font-size:15px">₹{{ (row.base + row.adj).toLocaleString('en-IN') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </motion.div>

    <!-- ---- Tasks ---- -->
    <motion.div v-else key="tasks"
      :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }" :transition="pageTransition(reduced)">
      <div class="section-title">Assigned tasks</div>
      <div v-for="(t, i) in tasks" :key="t.id" class="card item">
        <div class="item-row">
          <span class="item-ic" :class="taskIconClass(t.status)">
            <component :is="taskIcon(t.status)" :size="17" :stroke-width="2.25" />
          </span>
          <div>
            <div class="t">{{ t.title }}</div>
            <div class="d">Due {{ t.due }}</div>
          </div>
        </div>
        <span class="badge" :class="taskBadgeClass(t.status)"><span class="dot"></span>{{ t.status }}</span>
      </div>
    </motion.div>
  </AnimatePresence>
</template>

<script setup>
import { ref, computed } from 'vue'
import { motion, AnimatePresence } from 'motion-v'
import {
  CalendarDays, Calendar, CalendarCheck, CalendarX,
  Gauge, TrendingUp, Award, ShieldAlert, Wallet, ListChecks,
  CircleCheck, CircleDashed, CircleAlert,
} from 'lucide-vue-next'
import { auth } from '../auth'
import { usePrefersReducedMotion, pageTransition } from '../motion'

const reduced = usePrefersReducedMotion()

const TABS = [
  { key: 'attendance', label: 'Attendance', icon: CalendarDays },
  { key: 'performance', label: 'Performance', icon: Gauge },
  { key: 'salary', label: 'Salary', icon: Wallet },
  { key: 'tasks', label: 'Tasks', icon: ListChecks },
]
const activeTab = ref('attendance')

// ---- Attendance (mock) — deterministic pattern for the current calendar
// month so the page has stable, believable content without a real HR feed ----
const now = new Date()
const monthLabel = now.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
const leadingBlanks = new Date(now.getFullYear(), now.getMonth(), 1).getDay()

const attendanceDays = computed(() => {
  const year = now.getFullYear(), month = now.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const today = now.getDate()
  const out = []
  for (let d = 1; d <= daysInMonth; d++) {
    if (d > today) { out.push({ day: d, status: 'upcoming' }); continue }
    const dow = new Date(year, month, d).getDay()
    if (dow === 0) { out.push({ day: d, status: 'off' }); continue }
    const seed = (d * 7) % 11
    let status = 'present'
    if (seed === 0) status = 'leave'
    else if (seed === 3) status = 'absent'
    out.push({ day: d, status })
  }
  return out
})
const attendanceCounts = computed(() => {
  const c = { present: 0, leave: 0, absent: 0 }
  attendanceDays.value.forEach((d) => { if (c[d.status] !== undefined) c[d.status]++ })
  return c
})

// ---- Performance (mock) ----
const performance = {
  score: 84,
  overspeedCount: 3,
  trend: 'Improving vs last month',
  flags: [
    { label: 'Harsh braking', detail: 'Sudden deceleration events flagged by telemetry', count: 4, severity: 'warning', icon: ShieldAlert },
    { label: 'Rapid acceleration', detail: 'Sharp throttle events', count: 1, severity: 'warning', icon: TrendingUp },
    { label: 'Smooth driving streak', detail: 'Consecutive days with no violations', count: '6 days', severity: 'info', icon: Award },
  ],
}

// ---- Salary (mock) ----
function lastMonths(n) {
  const out = []
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    out.push(d.toLocaleDateString(undefined, { month: 'short', year: 'numeric' }))
  }
  return out
}
const salary = lastMonths(6).map((month, i) => ({
  month,
  base: 28000,
  adj: [1500, -500, 2000, 0, -1000, 1800][i] ?? 0,
}))

// ---- Tasks (mock) ----
const tasks = [
  { id: 1, title: 'Submit weekly vehicle inspection checklist', due: 'Today', status: 'Pending' },
  { id: 2, title: 'Complete defensive driving refresher module', due: 'Aug 6', status: 'In Progress' },
  { id: 3, title: 'Return fuel card receipts to dispatch', due: 'Aug 2', status: 'Done' },
  { id: 4, title: 'Acknowledge updated route safety policy', due: 'Aug 9', status: 'Pending' },
]
function taskIcon(status) { return status === 'Done' ? CircleCheck : status === 'In Progress' ? CircleDashed : CircleAlert }
function taskIconClass(status) { return status === 'Done' ? 'on' : status === 'In Progress' ? 'info' : 'warning' }
function taskBadgeClass(status) { return status === 'Done' ? 'active' : status === 'In Progress' ? 'info' : 'warning' }
</script>

<style scoped>
.ptabs { display: flex; gap: 8px; overflow-x: auto; margin-bottom: 18px; -webkit-overflow-scrolling: touch; }
.ptabs::-webkit-scrollbar { display: none; }
.ptab {
  flex: none; display: flex; align-items: center; gap: 7px;
  padding: 10px 16px; border-radius: var(--radius-pill); font-size: 13px; font-weight: 700;
  background: var(--surface); border: 1px solid var(--border); color: var(--muted);
}
.ptab:hover { color: var(--text); background: var(--surface-2); }
.ptab.active { background: var(--accent-grad); color: #fff; border-color: transparent; box-shadow: var(--shadow-brand); }

.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
.cal-dow { margin-bottom: 8px; text-align: center; color: var(--muted); font-size: 11px; font-weight: 700; text-transform: uppercase; }
.cal-cell {
  aspect-ratio: 1; display: grid; place-items: center; border-radius: 9px; font-size: 12.5px; font-weight: 700;
  background: var(--surface-2); color: var(--text);
}
.cal-cell.blank { background: none; }
.cal-cell.st-present { background: var(--green-soft); color: var(--green-strong); }
.cal-cell.st-leave { background: var(--amber-soft); color: var(--amber-strong); }
.cal-cell.st-absent { background: var(--crit-soft); color: var(--crit-strong); }
.cal-cell.st-off { background: var(--surface-3); color: var(--muted); }
.cal-cell.st-upcoming { background: none; border: 1px dashed var(--border); color: var(--muted); }
.cal-legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 14px; }
.cal-legend span { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); font-weight: 600; }
.cal-legend .dot { width: 9px; height: 9px; border-radius: 3px; display: inline-block; }
.cal-legend .st-present { background: var(--green-strong); }
.cal-legend .st-leave { background: var(--amber-strong); }
.cal-legend .st-absent { background: var(--crit-strong); }
.cal-legend .st-off { background: var(--surface-3); border: 1px solid var(--border); }
.cal-legend .st-upcoming { background: none; border: 1px dashed var(--border); }

.pay-table { width: 100%; border-collapse: collapse; min-width: 480px; }
.pay-table th {
  text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted);
  font-weight: 700; padding: 12px 14px; border-bottom: 1px solid var(--border);
}
.pay-table td { padding: 13px 14px; border-bottom: 1px solid var(--border); font-weight: 600; font-variant-numeric: tabular-nums; }
.pay-table tr:last-child td { border-bottom: none; }
</style>
