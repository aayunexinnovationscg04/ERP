<template>
  <div class="pf-grid">
      <!-- identity (real account + driver record) -->
      <section class="card flush pf-id" aria-label="Your details">
        <div class="card-head">
          <div class="card-head-title"><UserRound :size="18" /><h2>Details</h2></div>
        </div>
        <div class="id-top">
          <span class="id-avatar">{{ initials }}</span>
          <div class="id-text">
            <div class="id-name">{{ displayName }}</div>
            <div class="id-sub">@{{ auth.user?.username }}<template v-if="auth.user?.company?.name"> · {{ auth.user.company.name }}</template></div>
          </div>
        </div>
        <div v-if="detailsLoading" class="card-body" style="padding-top:0">
          <div class="skel skel-line lg"></div><div class="skel skel-line md"></div>
        </div>
        <div v-else class="list id-list">
          <div class="list-row">
            <span class="icon-chip"><Truck :size="16" /></span>
            <div class="grow"><div class="k">Assigned truck</div><div class="title">{{ vehicle ? vehicle.registration_number : 'None yet' }}</div></div>
            <router-link v-if="vehicle" to="/" class="row-link" aria-label="Open my truck" title="Open my truck"><ChevronRight :size="18" /></router-link>
          </div>
          <div v-if="driver?.phone || auth.user?.phone" class="list-row">
            <span class="icon-chip"><Phone :size="16" /></span>
            <div class="grow"><div class="k">Phone</div><div class="title num">{{ driver?.phone || auth.user?.phone }}</div></div>
          </div>
          <div v-if="driver?.license_no" class="list-row">
            <span class="icon-chip"><IdCard :size="16" /></span>
            <div class="grow"><div class="k">Driving licence</div><div class="title num">{{ driver.license_no }}</div></div>
          </div>
          <div v-if="auth.user?.email" class="list-row">
            <span class="icon-chip"><Mail :size="16" /></span>
            <div class="grow"><div class="k">Email</div><div class="title">{{ auth.user.email }}</div></div>
          </div>
        </div>
      </section>

      <!-- settings -->
      <section class="card pf-settings" aria-label="App settings">
        <div class="card-head">
          <div class="card-head-title"><Settings :size="18" /><h2>Settings</h2></div>
        </div>
        <div class="card-body set-body">
          <div class="set-row">
            <span class="k">Appearance</span>
            <div class="seg" role="radiogroup" aria-label="Theme">
              <button type="button" role="radio" :class="{ on: theme === 'light' }" :aria-checked="theme === 'light'" @click="setTheme('light')"><Sun :size="15" /> Light</button>
              <button type="button" role="radio" :class="{ on: theme === 'dark' }" :aria-checked="theme === 'dark'" @click="setTheme('dark')"><Moon :size="15" /> Dark</button>
            </div>
          </div>
          <button type="button" class="danger block pf-logout" @click="logout"><LogOut :size="16" /> Log out</button>
        </div>
      </section>

    <!-- records (sample data until the HR feed is connected) -->
    <section class="card flush pf-records" aria-label="Records">
      <div class="card-head">
        <div class="seg pf-tabs" role="tablist" aria-label="Profile sections">
          <button v-for="t in TABS" :key="t.key" type="button" role="tab" :class="{ on: activeTab === t.key }"
            :aria-selected="activeTab === t.key" @click="activeTab = t.key">
            <component :is="t.icon" :size="15" /> {{ t.label }}
          </button>
        </div>
        <span class="preview-tag" title="HR records are not connected yet — figures shown are sample data."><FlaskConical :size="13" /><span class="pt-text">Sample data</span></span>
      </div>

      <!-- Attendance -->
      <div v-if="activeTab === 'attendance'" key="attendance" class="card-body tab-in">
        <div class="kpis">
          <StatTile label="Present" :value="attendanceCounts.present" unit="days" :icon="CalendarCheck" tone="green" />
          <StatTile label="Leave" :value="attendanceCounts.leave" unit="days" :icon="CalendarMinus" tone="amber" />
          <StatTile label="Absent" :value="attendanceCounts.absent" unit="days" :icon="CalendarX" tone="red" />
        </div>
        <div class="cal-wrap">
          <h3 class="cal-head">{{ monthLabel }}</h3>
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

      <!-- Performance -->
      <div v-else-if="activeTab === 'performance'" key="performance" class="tab-in">
        <div class="card-body">
          <div class="score-top">
            <div>
              <div class="k">Driving score</div>
              <div class="score num">{{ performance.score }}<small>/100</small></div>
            </div>
            <span class="badge" :class="scoreTone">{{ scoreLabel }}</span>
          </div>
          <div class="meter score-bar" role="img" :aria-label="`Score ${performance.score} out of 100`"><span :style="{ width: performance.score + '%' }" :class="scoreTone === 'warning' ? 'amber' : scoreTone === 'critical' ? 'crit' : 'green'"></span></div>
          <div class="kvs" style="margin-top:16px">
            <div><span class="k">Overspeed</span><span class="v num">{{ performance.overspeedCount }} <small class="muted">this month</small></span></div>
            <div><span class="k">Trend</span><span class="v">{{ performance.trend }}</span></div>
          </div>
        </div>
        <div class="sub-head">Behaviour flags</div>
        <div class="list">
          <div v-for="(f, i) in performance.flags" :key="i" class="list-row">
            <span class="icon-chip" :class="f.severity === 'warning' ? 'amber' : 'green'"><component :is="f.icon" :size="16" /></span>
            <div class="grow"><div class="title">{{ f.label }}</div><div class="sub">{{ f.detail }}</div></div>
            <span class="badge plain" :class="f.severity === 'warning' ? 'warning' : 'green'">{{ f.count }}</span>
          </div>
        </div>
      </div>

      <!-- Salary -->
      <div v-else-if="activeTab === 'salary'" key="salary" class="tab-in">
        <div class="card-body pay-latest">
          <div class="k">Latest net pay · {{ salary[salary.length - 1].month }}</div>
          <div class="score num">₹{{ inr(net(salary[salary.length - 1])) }}</div>
        </div>
        <div class="sub-head">Pay history</div>
        <div class="list">
          <div v-for="row in [...salary].reverse()" :key="row.month" class="list-row">
            <span class="icon-chip"><Wallet :size="16" /></span>
            <div class="grow">
              <div class="title">{{ row.month }}</div>
              <div class="sub num">Base ₹{{ inr(row.base) }} ·
                <span :class="row.adj > 0 ? 'pos' : row.adj < 0 ? 'neg' : ''">{{ row.adj > 0 ? '+' : row.adj < 0 ? '−' : '' }}₹{{ inr(Math.abs(row.adj)) }} {{ row.adj >= 0 ? 'bonus' : 'deduction' }}</span>
              </div>
            </div>
            <div class="pay-num num">₹{{ inr(net(row)) }}</div>
          </div>
        </div>
      </div>

      <!-- Tasks -->
      <div v-else key="tasks" class="list tab-in">
        <div v-for="t in tasks" :key="t.id" class="list-row">
          <span class="icon-chip" :class="TASK[t.status].tone"><component :is="TASK[t.status].icon" :size="16" /></span>
          <div class="grow"><div class="title task-title">{{ t.title }}</div><div class="sub">Due {{ t.due }}</div></div>
          <span class="badge plain" :class="TASK[t.status].badge">{{ t.status }}</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  CalendarDays, CalendarCheck, FlaskConical, UserRound, CalendarX, CalendarMinus, Gauge, TrendingUp, Award, ShieldAlert, Wallet, ListChecks,
  CircleCheck, CircleDashed, CircleAlert, Truck, Phone, IdCard, Mail, ChevronRight, Settings, Sun, Moon, LogOut, Info,
} from 'lucide-vue-next'
import { auth, logout as endSession } from '../auth'
import { getMyVehicle, getSummary } from '../api'
import { useTheme } from '../theme'
import StatTile from '../components/StatTile.vue'

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
const scoreTone = computed(() => (performance.score >= 80 ? 'green' : performance.score >= 60 ? 'warning' : 'critical'))
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
  Done: { icon: CircleCheck, tone: 'green', badge: 'green' },
  'In Progress': { icon: CircleDashed, tone: 'info', badge: 'info' },
  Pending: { icon: CircleAlert, tone: 'amber', badge: 'warning' },
}
</script>

<style scoped>
.pf-grid {
  display: grid; gap: 16px; grid-template-columns: minmax(0, 1fr); align-items: start;
  grid-template-areas: "id" "rec" "set";
}
.pf-id { grid-area: id; }
.pf-records { grid-area: rec; }
.pf-settings { grid-area: set; }
@media (min-width: 1200px) {
  .pf-grid { grid-template-columns: 340px minmax(0, 1fr); grid-template-rows: auto 1fr; grid-template-areas: "id rec" "set rec"; }
}

.id-top { display: flex; align-items: center; gap: 14px; padding: 16px 18px; }
.id-avatar {
  flex: none; width: 52px; height: 52px; border-radius: 50%; display: grid; place-items: center;
  background: var(--navy-800); color: #FFFFFF; font-size: 1.125rem; font-weight: 800;
}
:root[data-theme="dark"] .id-avatar { background: var(--navy-600); }
.id-text { min-width: 0; }
.id-name { font-size: 1.0625rem; font-weight: 800; color: var(--ink-strong); line-height: 1.25; overflow-wrap: anywhere; }
.id-sub { color: var(--muted); font-size: 13px; margin-top: 2px; overflow-wrap: anywhere; }
.id-list { border-top: 1px solid var(--border); }
.id-list .title { white-space: normal; overflow-wrap: anywhere; }
.k { font-size: 12px; font-weight: 600; color: var(--muted); }

.set-body { display: flex; flex-direction: column; gap: 16px; }
.set-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }

.pf-tabs { flex-wrap: wrap; }
.tab-in { animation: page-in .16s cubic-bezier(.4, 0, .2, 1) both; }
.sub-head {
  padding: 10px 18px; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); background: var(--surface-2);
  font-size: .72rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; color: var(--muted);
}
.task-title { white-space: normal; }

.cal-head { margin: 4px 0 10px; }
.cal-wrap { max-width: 560px; }
.cal-grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 6px; }
.cal-dow { margin-bottom: 6px; text-align: center; color: var(--muted); font-size: 12px; font-weight: 700; }
.cal-cell {
  aspect-ratio: 1; max-height: 52px; display: grid; place-items: center; border-radius: var(--radius-sm);
  font-size: 13px; font-weight: 700; background: var(--surface-2); color: var(--text); font-variant-numeric: tabular-nums;
}
.cal-cell.blank { background: none; }
.cal-cell.st-present { background: var(--green-soft); color: var(--green); }
.cal-cell.st-leave { background: var(--amber-soft); color: var(--amber); }
.cal-cell.st-absent { background: var(--crit-soft); color: var(--crit); }
.cal-cell.st-off { background: var(--surface-3); color: var(--muted); }
.cal-cell.st-upcoming { background: none; border: 1px dashed var(--border-strong); color: var(--muted); }
.cal-cell.today { outline: 2px solid var(--brand); outline-offset: 1px; }
.cal-legend { display: flex; flex-wrap: wrap; gap: 8px 16px; margin-top: 14px; }
.cal-legend span { display: inline-flex; align-items: center; gap: 6px; font-size: 12.5px; color: var(--muted); font-weight: 600; }
.cal-legend .lg { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.lg.st-present { background: var(--green); }
.lg.st-leave { background: var(--amber); }
.lg.st-absent { background: var(--crit); }
.lg.st-off { background: var(--surface-3); border: 1px solid var(--border-strong); }

.score-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.score { font-size: 2rem; font-weight: 800; letter-spacing: -.02em; line-height: 1.1; color: var(--ink-strong); margin-top: 2px; }
.score small { font-size: 14px; font-weight: 700; color: var(--muted); letter-spacing: 0; margin-left: 2px; }
.score-bar { height: 8px; margin-top: 12px; }
.pos { color: var(--green); font-weight: 700; }
.neg { color: var(--red); font-weight: 700; }
.pay-num { flex: none; font-weight: 800; font-size: 15px; color: var(--ink-strong); white-space: nowrap; }
@media (max-width: 720px) {
  .pf-tabs { width: 100%; }
  .pf-tabs button { flex: 1 1 40%; }
  .id-top { padding: 14px; }
  .sub-head { padding: 10px 14px; }
}
</style>
