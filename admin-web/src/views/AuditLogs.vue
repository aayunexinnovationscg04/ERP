<!--
  Audit logs: every action a dealer (or manager) or pilot account takes —
  sign-ins/outs and every change, with before/after values. Switch Dealer /
  Pilot at the top, filter by account, company, action and time; click a row
  for the full change and that account's timeline in a right-hand panel.
-->
<template>
  <PageHeader>
    <button type="button" class="btn" :disabled="loading" @click="load()"><RefreshCw :size="16" :class="{ spin: loading }" /> Refresh</button>
  </PageHeader>

  <div class="seg role-switch" role="tablist" aria-label="Whose actions">
    <button v-for="r in roles" :key="r.key" type="button" role="tab" :aria-selected="role === r.key" :class="{ on: role === r.key }" @click="role = r.key">
      <component :is="r.icon" :size="16" /> {{ r.label }}
    </button>
  </div>

  <div class="stats">
    <StatCard label="Actions" :value="fmt(total)" :icon="ScrollText" tone="navy" :loading="loading && !rows.length" />
    <StatCard label="Changes" :value="fmt(pageStats.changes)" :icon="PencilLine" tone="info" :loading="loading && !rows.length" />
    <StatCard label="Sign-ins" :value="fmt(pageStats.signins)" :icon="LogIn" tone="green" :loading="loading && !rows.length" />
    <StatCard label="Failed sign-ins" :value="fmt(pageStats.failed)" :icon="ShieldX" :tone="pageStats.failed ? 'red' : 'navy'" :loading="loading && !rows.length" />
  </div>

  <div class="card">
    <div class="toolbar">
      <label class="input-icon">
        <Search :size="16" />
        <input v-model="q" class="input" type="search" placeholder="Search actions" aria-label="Search actions" />
      </label>
      <select v-model="actor" class="select" :aria-label="role === 'pilot' ? 'Filter by pilot' : 'Filter by dealer'">
        <option value="">{{ role === 'pilot' ? 'All pilots' : 'All dealers' }}</option>
        <option v-for="u in accounts" :key="u.id" :value="String(u.id)">{{ u.username }}</option>
      </select>
      <select v-model="company" class="select" aria-label="Filter by company">
        <option value="">All companies</option>
        <option v-for="c in companies" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
      </select>
      <select v-model="kind" class="select" aria-label="Filter by action">
        <option v-for="k in kinds" :key="k.key" :value="k.key">{{ k.label }}</option>
      </select>
    </div>
    <div class="toolbar time-bar">
      <div class="seg" role="group" aria-label="Time range">
        <button v-for="t in ranges" :key="t.key" type="button" :class="{ on: range === t.key }" @click="range = t.key">{{ t.label }}</button>
      </div>
      <template v-if="range === 'custom'">
        <input v-model="from" class="input date" type="date" aria-label="From date" :max="to || today" />
        <span class="muted">to</span>
        <input v-model="to" class="input date" type="date" aria-label="To date" :min="from" :max="today" />
      </template>
      <button v-if="filtersOn" type="button" class="btn btn-ghost btn-sm" @click="clearFilters"><X :size="14" /> Clear</button>
    </div>

    <div class="table-wrap">
      <table class="table stack audit-table">
        <thead><tr><th>Time</th><th>{{ role === 'pilot' ? 'Pilot' : 'Dealer' }}</th><th>Action</th><th class="col-target">Item</th><th aria-label="Open"></th></tr></thead>
        <TableSkeleton v-if="loading && !rows.length" :cols="5" :rows="8" />
        <tbody v-else-if="loadError">
          <tr class="table-empty"><td colspan="5"><EmptyState :icon="CircleAlert" title="Logs could not be loaded"><button type="button" class="btn" @click="load()">Try again</button></EmptyState></td></tr>
        </tbody>
        <tbody v-else-if="!rows.length">
          <tr class="table-empty"><td colspan="5">
            <EmptyState :icon="ScrollText" :title="filtersOn ? 'No matching actions' : 'No actions yet'">
              <button v-if="filtersOn" type="button" class="btn" @click="clearFilters">Clear filters</button>
            </EmptyState>
          </td></tr>
        </tbody>
        <tbody v-else>
          <tr v-for="r in rows" :key="r.id" class="row-link" :class="{ sel: open?.id === r.id }" tabindex="0"
              @click="openRow(r)" @keydown.enter="openRow(r)">
            <td data-label="Time" class="nowrap" :title="fmtDateTime(r.at)">
              <div class="t-primary num">{{ clock(r.at) }}</div><div class="t-secondary">{{ dayLabel(r.at) }}</div>
            </td>
            <td class="cell-head">
              <div class="cell-entity">
                <span class="entity-mark round">{{ (r.actor_username || '?')[0] }}</span>
                <div><div class="t-primary">{{ r.actor_username || '—' }}</div><div class="t-secondary">{{ r.company_name || '—' }}</div></div>
              </div>
            </td>
            <td data-label="Action" class="cell-action">
              <span class="act" :class="meta(r).tone"><component :is="meta(r).icon" :size="13" /> {{ meta(r).label }}</span>
              <div class="t-secondary summary">{{ r.summary }}</div>
            </td>
            <td data-label="Item" class="col-target">{{ r.target_label || '—' }}</td>
            <td class="t-right go" aria-hidden="true"><ChevronRight :size="16" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="total > 0" class="pager">
      <div class="pager-size">
        <span>{{ offset + 1 }}–{{ Math.min(total, offset + size) }} of {{ fmt(total) }}</span>
        <select v-model.number="size" class="select" aria-label="Rows per page">
          <option v-for="n in [25, 50, 100]" :key="n" :value="n">{{ n }} / page</option>
        </select>
      </div>
      <div class="pager-nav">
        <button type="button" class="pager-btn" :disabled="offset === 0" aria-label="Previous page" @click="offset -= size"><ChevronLeft :size="16" /></button>
        <button type="button" class="pager-btn" :disabled="offset + size >= total" aria-label="Next page" @click="offset += size"><ChevronRight :size="16" /></button>
      </div>
    </div>
  </div>

  <!-- right panel: one action in full + that account's timeline -->
  <Teleport to="body">
    <Transition name="panel">
      <div v-if="open" class="panel-root" @keydown.esc="open = null">
        <div class="panel-scrim" @click="open = null"></div>
        <aside ref="panelEl" class="panel" role="dialog" aria-modal="true" aria-labelledby="panel-title" tabindex="-1">
          <header class="panel-head">
            <span class="act lg" :class="meta(open).tone"><component :is="meta(open).icon" :size="16" /></span>
            <div class="panel-title-wrap">
              <h2 id="panel-title">{{ meta(open).label }}</h2>
              <p>{{ open.summary }}</p>
            </div>
            <button type="button" class="tb-btn" aria-label="Close panel" @click="open = null"><X :size="18" /></button>
          </header>

          <div class="panel-body">
            <dl class="facts">
              <div><dt>When</dt><dd>{{ fmtDateTime(open.at) }} <span class="muted">· {{ relTime(open.at) }}</span></dd></div>
              <div><dt>{{ role === 'pilot' ? 'Pilot' : 'Account' }}</dt><dd>{{ open.actor_username || '—' }} <span class="muted">· {{ roleLabel(open.actor_role) }}</span></dd></div>
              <div><dt>Company</dt><dd>{{ open.company_name || '—' }}</dd></div>
              <div v-if="open.target_label"><dt>Item</dt><dd>{{ open.target_label }}</dd></div>
              <div><dt>Result</dt><dd><span class="badge" :class="open.ok ? 'success' : 'danger'"><span class="bdot"></span>{{ open.ok ? 'Done' : 'Failed' }}</span></dd></div>
              <div><dt>Device</dt><dd>{{ device(open.user_agent) }}<template v-if="open.ip"> <span class="muted">· {{ open.ip }}</span></template></dd></div>
            </dl>

            <section v-if="changeRows(open).length" class="block">
              <h3>Changes</h3>
              <table class="changes">
                <thead><tr><th>Field</th><th>Before</th><th>After</th></tr></thead>
                <tbody>
                  <tr v-for="c in changeRows(open)" :key="c.field">
                    <td>{{ c.label }}</td><td class="old">{{ c.before }}</td><td class="new">{{ c.after }}</td>
                  </tr>
                </tbody>
              </table>
            </section>

            <section class="block">
              <div class="block-head">
                <h3>Timeline · {{ open.actor_username }}</h3>
                <button v-if="open.actor && actor !== String(open.actor)" type="button" class="btn btn-ghost btn-sm" @click="onlyThis(open)">Only this account</button>
              </div>
              <div v-if="timelineLoading" class="skel skel-line" style="height:120px"></div>
              <ol v-else class="timeline">
                <li v-for="t in timeline" :key="t.id" :class="{ cur: t.id === open.id }">
                  <button type="button" class="tl-item" @click="open = t">
                    <span class="tl-dot" :class="meta(t).tone"></span>
                    <span class="tl-main">
                      <span class="tl-sum">{{ t.summary }}</span>
                      <span class="tl-time">{{ fmtDateTime(t.at) }}</span>
                    </span>
                  </button>
                </li>
              </ol>
            </section>
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import {
  BellRing, ChevronLeft, ChevronRight, CircleAlert, Cpu, Hexagon, LogIn, LogOut, MapPin, Navigation, PencilLine,
  RefreshCw, ScrollText, Search, ShieldX, Truck, X,
} from 'lucide-vue-next'
import { getAudit, getCompanies, getUsers } from '../api'
import { fmt, fmtDateTime, relTime, roleLabel } from '../format'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import TableSkeleton from '../components/TableSkeleton.vue'

const roles = [
  { key: 'dealer', label: 'Dealer logs', icon: Truck },
  { key: 'pilot', label: 'Pilot logs', icon: Navigation },
]
const kinds = [
  { key: '', label: 'All actions' },
  { key: 'auth', label: 'Sign-ins & sign-outs' },
  { key: 'geofence', label: 'Geofences' },
  { key: 'vehicle', label: 'Vehicles' },
  { key: 'alert', label: 'Alerts' },
  { key: 'device', label: 'Device commands' },
  { key: 'api', label: 'Other changes' },
]
const ranges = [
  { key: 'today', label: 'Today' }, { key: '7', label: '7 days' }, { key: '30', label: '30 days' },
  { key: 'all', label: 'All time' }, { key: 'custom', label: 'Custom' },
]

const role = ref('dealer')
const q = ref(''); const actor = ref(''); const company = ref(''); const kind = ref('')
const range = ref('7'); const from = ref(''); const to = ref('')
const size = ref(25); const offset = ref(0)
const rows = ref([]); const total = ref(0); const stats = ref({ changes: 0, signins: 0, failed: 0 }); const loading = ref(true); const loadError = ref(false)
const users = ref([]); const companies = ref([])

const pad = (n) => String(n).padStart(2, '0')
const ymd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
const today = ymd(new Date())
const daysAgo = (n) => { const d = new Date(); d.setDate(d.getDate() - n); return ymd(d) }

const accounts = computed(() => users.value
  .filter((u) => (role.value === 'pilot' ? u.role === 'pilot' : ['dealer', 'manager'].includes(u.role)))
  .sort((a, b) => a.username.localeCompare(b.username)))
const filtersOn = computed(() => !!(q.value || actor.value || company.value || kind.value || range.value !== '7'))
function clearFilters() { q.value = ''; actor.value = ''; company.value = ''; kind.value = ''; range.value = '7'; from.value = ''; to.value = '' }

function params() {
  const p = { role: role.value, limit: size.value, offset: offset.value }
  if (q.value.trim()) p.q = q.value.trim()
  if (actor.value) p.actor = actor.value
  if (company.value) p.company = company.value
  if (kind.value) p.action = kind.value
  if (range.value === 'today') p.from = today
  else if (range.value === '7') p.from = daysAgo(6)
  else if (range.value === '30') p.from = daysAgo(29)
  else if (range.value === 'custom') { if (from.value) p.from = from.value; if (to.value) p.to = to.value }
  return p
}

let seq = 0
async function load() {
  const mine = ++seq
  loading.value = true
  try {
    const d = await getAudit(params())
    if (mine !== seq) return  // a newer request superseded this one
    rows.value = d.results; total.value = d.count; stats.value = d.stats || stats.value; loadError.value = false
  } catch (e) {
    if (mine === seq) loadError.value = true
  } finally { if (mine === seq) loading.value = false }
}

// any filter change -> back to page 1 (search is debounced)
let qTimer
watch(q, () => { clearTimeout(qTimer); qTimer = setTimeout(() => { offset.value = 0; load() }, 300) })
watch([actor, company, kind, range, from, to, size], () => { offset.value = 0; load() })
watch(offset, load)
watch(role, () => { actor.value = ''; offset.value = 0; open.value = null; load() })

onMounted(async () => {
  load()
  try { ;[users.value, companies.value] = await Promise.all([getUsers(), getCompanies()]) } catch (e) { /* filters just stay short */ }
})

const pageStats = stats  // exact totals for the whole filtered set, from the API

const META = {
  'auth.login': { label: 'Signed in', icon: LogIn, tone: 'green' },
  'auth.login_failed': { label: 'Failed sign-in', icon: ShieldX, tone: 'red' },
  'auth.login_blocked': { label: 'Sign-in blocked', icon: ShieldX, tone: 'red' },
  'auth.logout': { label: 'Signed out', icon: LogOut, tone: 'gray' },
  'auth.logout_all': { label: 'Signed out everywhere', icon: LogOut, tone: 'gray' },
  'geofence.create': { label: 'Geofence created', icon: Hexagon, tone: 'info' },
  'geofence.update': { label: 'Geofence changed', icon: Hexagon, tone: 'info' },
  'geofence.delete': { label: 'Geofence deleted', icon: Hexagon, tone: 'red' },
  'vehicle.rename': { label: 'Vehicle renamed', icon: Truck, tone: 'info' },
  'alert.acknowledge': { label: 'Alert acknowledged', icon: BellRing, tone: 'amber' },
  'device.command': { label: 'Device command', icon: Cpu, tone: 'amber' },
}
const meta = (r) => META[r.action] || { label: 'Other change', icon: PencilLine, tone: 'gray' }

const FIELD = {
  name: 'Name', kind: 'Shape', purpose: 'Purpose', center_lat: 'Latitude', center_lng: 'Longitude',
  radius_m: 'Radius (m)', active: 'Active', local_name: 'Nickname', status: 'Status', command: 'Command',
}
const show = (v) => (v === null || v === undefined || v === '' ? '—' : v === true ? 'Yes' : v === false ? 'No' : String(v))
const changeRows = (r) => Object.entries(r.changes || {}).map(([k, [b, a]]) => ({ field: k, label: FIELD[k] || k, before: show(b), after: show(a) }))

function device(ua) {
  if (!ua) return '—'
  const os = /Android/.test(ua) ? 'Android' : /iPhone|iPad/.test(ua) ? 'iOS' : /Windows/.test(ua) ? 'Windows'
    : /Mac OS/.test(ua) ? 'macOS' : /Linux/.test(ua) ? 'Linux' : ''
  const br = /Edg\//.test(ua) ? 'Edge' : /Chrome\//.test(ua) ? 'Chrome' : /Firefox\//.test(ua) ? 'Firefox'
    : /Safari\//.test(ua) ? 'Safari' : /curl|python|axios|node/i.test(ua) ? 'Script' : 'Browser'
  return os ? `${br} on ${os}` : br
}
const clock = (s) => new Date(s).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
function dayLabel(s) {
  const d = ymd(new Date(s))
  return d === today ? 'Today' : d === daysAgo(1) ? 'Yesterday' : new Date(s).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}

// ---- right panel ----
const open = ref(null); const panelEl = ref(null)
const timeline = ref([]); const timelineLoading = ref(false)
let timelineFor = null
async function openRow(r) {
  open.value = r
  await nextTick(); panelEl.value?.focus({ preventScroll: true })
}
watch(open, async (r) => {
  document.body.style.overflow = r ? 'hidden' : ''
  if (!r || !r.actor || timelineFor === r.actor) return
  timelineFor = r.actor; timelineLoading.value = true
  try { timeline.value = (await getAudit({ actor: r.actor, limit: 100 })).results }
  catch (e) { timeline.value = [r] } finally { timelineLoading.value = false }
})
watch(open, (r) => { if (!r) timelineFor = null })
function onlyThis(r) { actor.value = String(r.actor); open.value = null }
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .8s linear infinite; }

.role-switch { display: flex; width: 100%; max-width: 420px; margin-bottom: 12px; padding: 4px; }
.role-switch button { flex: 1; justify-content: center; min-height: 38px; font-size: .875rem; }
.time-bar { border-bottom: 1px solid var(--border); padding-top: 0; }
.input.date { width: auto; min-width: 150px; }

.row-link { cursor: pointer; }
.row-link:focus-visible { outline: 2px solid var(--brand); outline-offset: -2px; }
.row-link.sel { background: var(--surface-2); }
.go { color: var(--muted-2); width: 36px; }
.summary { max-width: 52ch; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.col-target { color: var(--muted); max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.act {
  display: inline-flex; align-items: center; gap: 5px; height: 24px; padding: 0 9px; border-radius: 999px;
  font-size: .75rem; font-weight: 700; white-space: nowrap; background: var(--surface-3); color: var(--text);
}
.act.green { background: var(--green-soft); color: var(--green); }
.act.red { background: var(--red-soft); color: var(--red); }
.act.info { background: var(--info-soft); color: var(--info); }
.act.amber { background: var(--amber-soft); color: var(--amber); }
.act.gray { background: var(--surface-3); color: var(--muted); }
.act.lg { width: 38px; height: 38px; padding: 0; justify-content: center; border-radius: 10px; flex: none; }

/* right panel */
.panel-root { position: fixed; inset: 0; z-index: 100; }
.panel-scrim { position: absolute; inset: 0; background: rgba(7, 21, 36, .45); }
.panel {
  position: absolute; top: 0; right: 0; bottom: 0; width: min(480px, 100%); display: flex; flex-direction: column;
  background: var(--surface); border-left: 1px solid var(--border); box-shadow: var(--shadow-lg); outline: none;
}
.panel-head { display: flex; align-items: flex-start; gap: 12px; padding: 16px 18px; border-bottom: 1px solid var(--border); }
.panel-title-wrap { flex: 1; min-width: 0; }
.panel-head h2 { font-size: 1rem; font-weight: 800; }
.panel-head p { font-size: .8125rem; color: var(--muted); margin-top: 2px; overflow-wrap: anywhere; }
.panel-head .tb-btn { margin: -4px -6px 0 0; }
.panel-body { flex: 1; overflow-y: auto; padding: 16px 18px 28px; }
.facts { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 12px 16px; margin: 0; }
.facts dt { font-size: .68rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; color: var(--muted); }
.facts dd { margin: 3px 0 0; font-size: .8125rem; color: var(--text); overflow-wrap: anywhere; }
.block { margin-top: 20px; }
.block h3 { font-size: .8125rem; font-weight: 750; color: var(--ink-strong); margin-bottom: 8px; }
.block-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.block-head h3 { margin: 0; }
.changes { width: 100%; border-collapse: collapse; font-size: .8125rem; border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.changes th { text-align: left; padding: 7px 10px; font-size: .68rem; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); background: var(--surface-2); }
.changes td { padding: 8px 10px; border-top: 1px solid var(--border); overflow-wrap: anywhere; }
.changes .old { color: var(--muted); text-decoration: line-through; }
.changes .new { color: var(--ink-strong); font-weight: 650; }
.timeline { list-style: none; margin: 0; padding: 0 0 0 6px; border-left: 2px solid var(--border); }
.timeline li { position: relative; }
.tl-item {
  width: 100%; display: flex; align-items: flex-start; gap: 10px; padding: 8px 8px 8px 12px; margin-left: -7px;
  border: 0; border-radius: 8px; background: transparent; color: var(--text); text-align: left; cursor: pointer; box-shadow: none; transform: none;
}
.tl-item:hover { background: var(--surface-2); transform: none; }
.timeline li.cur .tl-item { background: var(--surface-3); }
.tl-dot { flex: none; width: 12px; height: 12px; margin-top: 3px; border-radius: 50%; padding: 0; border: 2px solid var(--surface); }
.tl-dot.green { background: var(--green); } .tl-dot.red { background: var(--red); } .tl-dot.info { background: var(--info); }
.tl-dot.amber { background: var(--amber); } .tl-dot.gray { background: var(--muted-2); }
.tl-main { display: flex; flex-direction: column; min-width: 0; }
.tl-sum { font-size: .8125rem; font-weight: 600; overflow-wrap: anywhere; }
.tl-time { font-size: .72rem; color: var(--muted); }

.panel-enter-active, .panel-leave-active { transition: opacity .18s var(--ease); }
.panel-enter-active .panel, .panel-leave-active .panel { transition: transform .2s var(--ease); }
.panel-enter-from, .panel-leave-to { opacity: 0; }
.panel-enter-from .panel, .panel-leave-to .panel { transform: translateX(24px); }

@media (max-width: 720px) {
  .role-switch { max-width: none; }
  .time-bar .seg { flex-basis: 100%; }
  .input.date { flex: 1 1 130px; min-width: 0; }
  .audit-table .go, .audit-table .col-target { display: none; }
  .audit-table td.cell-action { grid-column: 1 / -1; }
  .summary { max-width: none; white-space: normal; }
  .facts { grid-template-columns: minmax(0, 1fr); }
  .tl-item { min-height: 44px; }
}
</style>
