<template>
  <div class="page-head">
    <div class="ph-text">
      <h1>Profile</h1>
    </div>
  </div>

  <div class="pf-grid">
    <!-- identity (real account + driver record) -->
    <section class="card pf-id" aria-label="Your details">
      <div class="id-top">
        <span class="id-avatar">{{ initials }}</span>
        <div class="id-text">
          <div class="id-name">{{ displayName }}</div>
          <div class="id-sub">@{{ auth.user?.username }}<template v-if="auth.user?.company?.name"> · {{ auth.user.company.name }}</template></div>
        </div>
      </div>
      <div v-if="detailsLoading" class="card-pad" style="padding-top:0">
        <div class="skel skel-line lg"></div><div class="skel skel-line md"></div>
      </div>
      <ul v-else class="list id-list">
        <li class="list-row">
          <span class="row-ic ic-neutral"><Truck :size="19" :stroke-width="2.25" /></span>
          <div class="row-main"><div class="k">Assigned truck</div><div class="row-title">{{ vehicle ? vehicle.registration_number : 'None yet' }}</div></div>
          <router-link v-if="vehicle" to="/" class="btn btn-sm btn-ghost" aria-label="Open my truck"><ChevronRight :size="18" /></router-link>
        </li>
        <li v-if="driver?.phone || auth.user?.phone" class="list-row">
          <span class="row-ic ic-neutral"><Phone :size="19" :stroke-width="2.25" /></span>
          <div class="row-main"><div class="k">Phone</div><div class="row-title num">{{ driver?.phone || auth.user?.phone }}</div></div>
        </li>
        <li v-if="driver?.license_no" class="list-row">
          <span class="row-ic ic-neutral"><IdCard :size="19" :stroke-width="2.25" /></span>
          <div class="row-main"><div class="k">Driving licence</div><div class="row-title num">{{ driver.license_no }}</div></div>
        </li>
        <li v-if="auth.user?.email" class="list-row">
          <span class="row-ic ic-neutral"><Mail :size="19" :stroke-width="2.25" /></span>
          <div class="row-main"><div class="k">Email</div><div class="row-title">{{ auth.user.email }}</div></div>
        </li>
      </ul>
    </section>

    <!-- records (sample data until the HR feed is connected) -->
    <section class="pf-records" aria-label="Records">
      <div class="segmented pf-tabs" role="tablist" aria-label="Profile sections">
        <button v-for="t in TABS" :key="t.key" type="button" role="tab" class="seg-btn" :class="{ active: activeTab === t.key }"
          :aria-selected="activeTab === t.key" @click="activeTab = t.key">
          <component :is="t.icon" :size="17" :stroke-width="2.25" /><span>{{ t.label }}</span>
        </button>
      </div>
      <div class="notice" role="note" style="margin:12px 0 14px">
        <Info :size="16" :stroke-width="2.25" />
        <span><strong>Sample data</strong> · HR records not connected yet</span>
      </div>

      <AnimatePresence mode="wait">
        <!-- Attendance -->
        <motion.div v-if="activeTab === 'attendance'" key="attendance"
          :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }" :exit="{ opacity: 0 }" :transition="pageTransition(reduced)">
          <div class="stat-grid cols-3">
            <div class="stat tone-green">
              <div class="stat-top"><span class="stat-ic"><CalendarCheck :size="17" :stroke-width="2.25" /></span><span class="stat-label">Present</span></div>
              <div class="stat-value">{{ attendanceCounts.present }}<small>days</small></div>
            </div>
            <div class="stat tone-amber">
              <div class="stat-top"><span class="stat-ic"><CalendarMinus :size="17" :stroke-width="2.25" /></span><span class="stat-label">Leave</span></div>
              <div class="stat-value">{{ attendanceCounts.leave }}<small>days</small></div>
            </div>
            <div class="stat tone-red">
              <div class="stat-top"><span class="stat-ic"><CalendarX :size="17" :stroke-width="2.25" /></span><span class="stat-label">Absent</span></div>
              <div class="stat-value">{{ attendanceCounts.absent }}<small>days</small></div>
            </div>
          </div>

          <div class="card card-pad" style="margin-top:14px">
            <div class="cal-wrap">
            <div class="cal-head"><h2>{{ monthLabel }}</h2></div>
            <div class="cal-grid cal-dow" aria-hidden="true">
              <span v-for="(d, i) in ['S','M','T','W','T','F','S']" :key="i">{{ d }}</span>
            </div>
            <div class="cal-grid">
              <span v-for="n in leadingBlanks" :key="'b'+n" class="cal-cell blank"></span>
              <span v-for="d in attendanceDays" :key="d.day" class="cal-cell" :class="['st-' + d.status, { today: d.day === todayNum }]"
                :title="`${d.day}: ${STATUS_TEXT[d.status]}`" :aria-label="`${d.day}: ${STATUS_TEXT[d.status]}`">{{ d.day }}</span>
            </div>
            <div class="cal-legend">
              <span><i class="lg st-present"></i>Present</span>
              <span><i class="lg st-leave"></i>Leave</span>
              <span><i class="lg st-absent"></i>Absent</span>
              <span><i class="lg st-off"></i>Off</span>
            </div>
            </div>
          </div>
        </motion.div>

        <!-- Performance -->
        <motion.div v-else-if="activeTab === 'performance'" key="performance"
          :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }" :exit="{ opacity: 0 }" :transition="pageTransition(reduced)">
          <div class="card card-pad">
            <div class="score-top">
              <div>
                <div class="stat-label">Driving score</div>
                <div class="score num">{{ performance.score }}<small>/100</small></div>
              </div>
              <span class="badge badge-lg" :class="scoreTone">{{ scoreLabel }}</span>
            </div>
            <div class="bar" role="img" :aria-label="`Score ${performance.score} out of 100`"><span :style="{ width: performance.score + '%' }" :class="scoreTone"></span></div>
            <div class="stat-grid" style="margin-top:16px">
              <div class="stat tone-amber">
                <div class="stat-top"><span class="stat-ic"><Gauge :size="17" :stroke-width="2.25" /></span><span class="stat-label">Overspeed</span></div>
                <div class="stat-value">{{ performance.overspeedCount }}<small>this month</small></div>
              </div>
              <div class="stat tone-green">
                <div class="stat-top"><span class="stat-ic"><TrendingUp :size="17" :stroke-width="2.25" /></span><span class="stat-label">Trend</span></div>
                <div class="stat-value sm">{{ performance.trend }}</div>
              </div>
            </div>
          </div>
          <div class="section-title">Behaviour flags</div>
          <ul class="card list">
            <li v-for="(f, i) in performance.flags" :key="i" class="list-row">
              <span class="row-ic" :class="f.severity === 'warning' ? 'ic-amber' : 'ic-green'"><component :is="f.icon" :size="19" :stroke-width="2.25" /></span>
              <div class="row-main"><div class="row-title">{{ f.label }}</div><div class="row-sub">{{ f.detail }}</div></div>
              <span class="badge" :class="f.severity === 'warning' ? 'warning' : 'valid'">{{ f.count }}</span>
            </li>
          </ul>
        </motion.div>

        <!-- Salary -->
        <motion.div v-else-if="activeTab === 'salary'" key="salary"
          :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }" :exit="{ opacity: 0 }" :transition="pageTransition(reduced)">
          <div class="card card-pad pay-latest">
            <div class="stat-label">Latest net pay · {{ salary[salary.length - 1].month }}</div>
            <div class="score num">₹{{ inr(net(salary[salary.length - 1])) }}</div>
          </div>
          <div class="section-title">Pay history</div>
          <ul class="card list">
            <li v-for="row in [...salary].reverse()" :key="row.month" class="list-row">
              <span class="row-ic ic-neutral"><Wallet :size="19" :stroke-width="2.25" /></span>
              <div class="row-main">
                <div class="row-title">{{ row.month }}</div>
                <div class="row-sub num">Base ₹{{ inr(row.base) }} ·
                  <span :class="row.adj > 0 ? 'pos' : row.adj < 0 ? 'neg' : ''">{{ row.adj > 0 ? '+' : row.adj < 0 ? '−' : '' }}₹{{ inr(Math.abs(row.adj)) }} {{ row.adj >= 0 ? 'bonus' : 'deduction' }}</span>
                </div>
              </div>
              <div class="row-num">₹{{ inr(net(row)) }}</div>
            </li>
          </ul>
        </motion.div>

        <!-- Tasks -->
        <motion.div v-else key="tasks"
          :initial="{ opacity: 0, y: reduced ? 0 : 6 }" :animate="{ opacity: 1, y: 0 }" :exit="{ opacity: 0 }" :transition="pageTransition(reduced)">
          <ul class="card list">
            <li v-for="t in tasks" :key="t.id" class="list-row">
              <span class="row-ic" :class="TASK[t.status].tone"><component :is="TASK[t.status].icon" :size="19" :stroke-width="2.25" /></span>
              <div class="row-main"><div class="row-title">{{ t.title }}</div><div class="row-sub">Due {{ t.due }}</div></div>
              <span class="badge" :class="TASK[t.status].badge">{{ t.status }}</span>
            </li>
          </ul>
        </motion.div>
      </AnimatePresence>
    </section>

    <!-- settings -->
    <section class="card pf-settings" aria-label="App settings">
      <div class="card-head">
        <span class="ch-ic ic-neutral"><Settings :size="18" :stroke-width="2.25" /></span>
        <div class="ch-text"><h2>Settings</h2></div>
      </div>
      <div class="card-pad set-body">
        <div>
          <div class="k" style="margin-bottom:8px">Appearance</div>
          <div class="segmented" role="radiogroup" aria-label="Theme">
            <button type="button" role="radio" class="seg-btn" :class="{ active: theme === 'light' }" :aria-checked="theme === 'light'" @click="setTheme('light')"><Sun :size="17" :stroke-width="2.25" /><span>Light</span></button>
            <button type="button" role="radio" class="seg-btn" :class="{ active: theme === 'dark' }" :aria-checked="theme === 'dark'" @click="setTheme('dark')"><Moon :size="17" :stroke-width="2.25" /><span>Dark</span></button>
          </div>
        </div>
        <button type="button" class="btn btn-danger btn-block" @click="logout"><LogOut :size="18" :stroke-width="2.25" /> Log out</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { motion, AnimatePresence } from 'motion-v'
import {
  CalendarDays, CalendarCheck, CalendarX, CalendarMinus, Gauge, TrendingUp, Award, ShieldAlert, Wallet, ListChecks,
  CircleCheck, CircleDashed, CircleAlert, Truck, Phone, IdCard, Mail, ChevronRight, Settings, Sun, Moon, LogOut, Info,
} from 'lucide-vue-next'
import { auth, logout as endSession } from '../auth'
import { getMyVehicle, getSummary } from '../api'
import { useTheme } from '../theme'
import { usePrefersReducedMotion, pageTransition } from '../motion'

const reduced = usePrefersReducedMotion()
const router = useRouter()
const { theme, toggleTheme } = useTheme()
function setTheme(t) { if (theme.value !== t) toggleTheme() }
async function logout() { await endSession(); router.push('/login') }

// ---- identity: account from the session + driver record from /pilot/vehicle ----
const vehicle = ref(null)
const detailsLoading = ref(true)
const driver = computed(() => vehicle.value?.active_pilot || null)
const displayName = computed(() => {
  const u = auth.user || {}
  const full = [u.first_name, u.last_name].filter(Boolean).join(' ')
  return full || driver.value?.name || u.username || 'Pilot'
})
const initials = computed(() => displayName.value.split(/\s+/).map((w) => w[0]).join('').slice(0, 2).toUpperCase())
onMounted(async () => {
  // Ask the summary first: /pilot/vehicle answers 404 when no truck is assigned.
  try { vehicle.value = (await getSummary()).assigned ? await getMyVehicle() : null } catch (e) { vehicle.value = null }
  finally { detailsLoading.value = false }
})

const TABS = [
  { key: 'attendance', label: 'Attendance', icon: CalendarDays },
  { key: 'performance', label: 'Score', icon: Gauge },
  { key: 'salary', label: 'Pay', icon: Wallet },
  { key: 'tasks', label: 'Tasks', icon: ListChecks },
]
const activeTab = ref('attendance')

// ---- Attendance (sample): deterministic pattern for the current month ----
const now = new Date()
const todayNum = now.getDate()
const monthLabel = now.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })
const leadingBlanks = new Date(now.getFullYear(), now.getMonth(), 1).getDay()
const STATUS_TEXT = { present: 'Present', leave: 'Leave', absent: 'Absent', off: 'Weekly off', upcoming: 'Upcoming' }
const attendanceDays = computed(() => {
  const year = now.getFullYear(), month = now.getMonth()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const out = []
  for (let d = 1; d <= daysInMonth; d++) {
    if (d > todayNum) { out.push({ day: d, status: 'upcoming' }); continue }
    if (new Date(year, month, d).getDay() === 0) { out.push({ day: d, status: 'off' }); continue }
    const seed = (d * 7) % 11
    out.push({ day: d, status: seed === 0 ? 'leave' : seed === 3 ? 'absent' : 'present' })
  }
  return out
})
const attendanceCounts = computed(() => {
  const c = { present: 0, leave: 0, absent: 0 }
  attendanceDays.value.forEach((d) => { if (c[d.status] !== undefined) c[d.status]++ })
  return c
})

// ---- Performance (sample) ----
const performance = {
  score: 84,
  overspeedCount: 3,
  trend: 'Improving',
  flags: [
    { label: 'Harsh braking', detail: 'Sudden deceleration events', count: 4, severity: 'warning', icon: ShieldAlert },
    { label: 'Rapid acceleration', detail: 'Sharp throttle events', count: 1, severity: 'warning', icon: TrendingUp },
    { label: 'Smooth driving streak', detail: 'Consecutive days with no violations', count: '6 days', severity: 'info', icon: Award },
  ],
}
const scoreTone = computed(() => (performance.score >= 80 ? 'valid' : performance.score >= 60 ? 'warning' : 'critical'))
const scoreLabel = computed(() => (performance.score >= 80 ? 'Excellent' : performance.score >= 60 ? 'Needs attention' : 'At risk'))

// ---- Salary (sample) ----
function lastMonths(n) {
  const out = []
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    out.push(d.toLocaleDateString(undefined, { month: 'short', year: 'numeric' }))
  }
  return out
}
const salary = lastMonths(6).map((month, i) => ({ month, base: 28000, adj: [1500, -500, 2000, 0, -1000, 1800][i] ?? 0 }))
const net = (r) => r.base + r.adj
const inr = (n) => n.toLocaleString('en-IN')

// ---- Tasks (sample) ----
const tasks = [
  { id: 1, title: 'Submit weekly vehicle inspection checklist', due: 'Today', status: 'Pending' },
  { id: 2, title: 'Complete defensive driving refresher module', due: 'Aug 6', status: 'In Progress' },
  { id: 3, title: 'Return fuel card receipts to dispatch', due: 'Aug 2', status: 'Done' },
  { id: 4, title: 'Acknowledge updated route safety policy', due: 'Aug 9', status: 'Pending' },
]
const TASK = {
  Done: { icon: CircleCheck, tone: 'ic-green', badge: 'valid' },
  'In Progress': { icon: CircleDashed, tone: 'ic-info', badge: 'info' },
  Pending: { icon: CircleAlert, tone: 'ic-amber', badge: 'warning' },
}
</script>

<style scoped>
.pf-grid {
  display: grid; gap: 14px; grid-template-columns: minmax(0, 1fr);
  grid-template-areas: "id" "rec" "set";
}
.pf-id { grid-area: id; }
.pf-records { grid-area: rec; min-width: 0; }
.pf-settings { grid-area: set; }
@media (min-width: 1100px) {
  .pf-grid { grid-template-columns: 340px minmax(0, 1fr); grid-template-rows: auto 1fr; grid-template-areas: "id rec" "set rec"; gap: 18px; align-items: start; }
}

.id-top { display: flex; align-items: center; gap: 16px; padding: 18px; }
.id-avatar {
  flex: none; width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center;
  background: var(--navy-800); color: #FFFFFF; font-size: 1.375rem; font-weight: 800;
}
:root[data-theme="dark"] .id-avatar { background: var(--navy-600); }
.id-text { min-width: 0; }
.id-name { font-size: 1.25rem; font-weight: 800; color: var(--ink-strong); letter-spacing: -.01em; line-height: 1.2; overflow-wrap: anywhere; }
.id-sub { color: var(--muted); font-size: .875rem; margin-top: 2px; overflow-wrap: anywhere; }
.id-list { border-top: 1px solid var(--border); }
.k { font-size: .75rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; color: var(--muted); }

.pf-tabs .seg-btn { padding: 0 6px; }
@media (max-width: 519.98px) { .pf-tabs { grid-auto-flow: row; grid-template-columns: repeat(2, minmax(0, 1fr)); } }

.stat-grid.cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
@media (max-width: 400px) {
  .stat-grid.cols-3 .stat { padding: 12px 10px; }
  .stat-grid.cols-3 .stat-ic { display: none; }
  .stat-grid.cols-3 .stat-value { font-size: 1.5rem; }
}

.cal-head { margin-bottom: 12px; }
.cal-wrap { max-width: 560px; }
.cal-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 6px; }
.cal-dow { margin-bottom: 6px; text-align: center; color: var(--muted); font-size: .75rem; font-weight: 700; }
.cal-cell {
  aspect-ratio: 1; max-height: 56px; display: grid; place-items: center; border-radius: var(--radius-sm);
  font-size: .875rem; font-weight: 700; background: var(--surface-2); color: var(--text); font-variant-numeric: tabular-nums;
}
.cal-cell.blank { background: none; }
.cal-cell.st-present { background: var(--green-soft); color: var(--green); }
.cal-cell.st-leave { background: var(--amber-soft); color: var(--amber); }
.cal-cell.st-absent { background: var(--crit-soft); color: var(--crit); }
.cal-cell.st-off { background: var(--surface-3); color: var(--muted); }
.cal-cell.st-upcoming { background: none; border: 1px dashed var(--border-strong); color: var(--muted); }
.cal-cell.today { outline: 2px solid var(--brand); outline-offset: 1px; }
.cal-legend { display: flex; flex-wrap: wrap; gap: 8px 16px; margin-top: 14px; }
.cal-legend span { display: inline-flex; align-items: center; gap: 6px; font-size: .8125rem; color: var(--muted); font-weight: 600; }
.cal-legend .lg { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.lg.st-present { background: var(--green); }
.lg.st-leave { background: var(--amber); }
.lg.st-absent { background: var(--crit); }
.lg.st-off { background: var(--surface-3); border: 1px solid var(--border-strong); }

.score-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.score { font-size: 2.75rem; font-weight: 800; letter-spacing: -.03em; line-height: 1.05; color: var(--ink-strong); margin-top: 4px; }
.score small { font-size: 1rem; font-weight: 700; color: var(--muted); letter-spacing: 0; margin-left: 2px; }
.bar { height: 10px; border-radius: var(--radius-pill); background: var(--surface-3); margin-top: 14px; overflow: hidden; }
.bar span { display: block; height: 100%; border-radius: var(--radius-pill); background: var(--green); }
.bar span.warning { background: var(--amber); }
.bar span.critical { background: var(--crit); }

.pos { color: var(--green); font-weight: 700; }
.neg { color: var(--red); font-weight: 700; }
.row-num { font-size: 1.125rem; }

.set-body { display: flex; flex-direction: column; gap: 18px; }
.hint { font-size: .8125rem; color: var(--muted); margin-top: 8px; }
</style>
