<template>
  <PageHeader>
    <router-link to="/alerts" class="btn"><ShieldAlert :size="16" /> Fuel alerts</router-link>
  </PageHeader>

  <div v-if="loading" class="kpis"><div class="skel sk-chip" v-for="n in 4" :key="n"></div></div>
  <div v-else class="kpis">
    <StatTile label="Fuel in tanks" :value="withReading.length ? fmt(totalLitres, 0) : '—'" :unit="withReading.length ? 'L' : ''" :icon="Fuel" tone="brand" />
    <StatTile label="Average level" :value="avgPct == null ? '—' : avgPct" :unit="avgPct == null ? '' : '%'" :icon="Gauge" tone="blue" />
    <StatTile label="Low fuel" :value="lowCount" :icon="TriangleAlert" :tone="lowCount ? 'crit' : 'gray'" />
    <StatTile label="No reading yet" :value="vehicles.length - withReading.length" :icon="CircleDashed" tone="gray" />
  </div>

  <div v-if="loading" class="fuel-grid"><div class="skel sk-box" v-for="n in 6" :key="n"></div></div>

  <div v-else-if="!vehicles.length" class="card">
    <EmptyState :icon="Fuel" title="No vehicles yet" text="Shown once a fuel sensor reports." />
  </div>

  <template v-else>
    <div class="toolbar">
      <label class="search">
        <Search :size="16" />
        <input v-model="q" type="search" placeholder="Search vehicle…" aria-label="Search vehicles" />
      </label>
      <div class="seg" role="group" aria-label="Sort">
        <button :class="{ on: sort === 'level' }" @click="sort = 'level'">Lowest first</button>
        <button :class="{ on: sort === 'name' }" @click="sort = 'name'">A–Z</button>
      </div>
    </div>
    <div class="fuel-grid">
      <router-link v-for="v in pager.rows.value" :key="v.id" :to="`/fuel/${v.id}`" class="card fuel-box">
        <div class="fb-top">
          <div style="min-width:0">
            <div class="fb-name">{{ v.local_name }}</div>
            <div class="fb-reg">{{ v.registration_number }}</div>
          </div>
          <span class="badge" :class="levelBadge(v)">{{ levelText(v) }}</span>
        </div>
        <div class="fb-level">
          <template v-if="v.latest?.total_litres != null"><b class="num">{{ fmt(v.latest.total_litres) }}</b><span>L</span></template>
          <span v-else class="fb-none">— L</span>
          <span class="fb-pct" v-if="hasPct(v)">{{ pct(v) }}%</span>
        </div>
        <div class="meter"><span :class="levelClass(v)" :style="{ width: pct(v) + '%' }"></span></div>
        <div class="fb-foot">
          <span>{{ v.tank_capacity_litres ? v.tank_capacity_litres + ' L tank' : '—' }}</span>
          <span class="ico" style="gap:6px"><span class="dot" :class="freshness(v)"></span>{{ ago(v.latest?.received_at) }}</span>
        </div>
      </router-link>
    </div>
    <div v-if="!shown.length" class="card"><EmptyState compact :icon="SearchX" title="No matching vehicles" /></div>
    <div v-else class="card fv-pager"><Pager :pager="pager" /></div>
  </template>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { Fuel, Gauge, TriangleAlert, CircleDashed, Search, SearchX, ShieldAlert } from 'lucide-vue-next'
import { getVehicles } from '../api'
import { freshness, fmt, ago } from '../util'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const vehicles = ref([])
const loading = ref(true)
const q = ref('')
const sort = ref('level')
let timer

const hasPct = (v) => !!v.tank_capacity_litres && v.latest?.total_litres != null
function pct(v) {
  if (!hasPct(v)) return 0
  return Math.max(0, Math.min(100, Math.round((v.latest.total_litres / v.tank_capacity_litres) * 100)))
}
// Colour only when there's a real reading — no telemetry stays neutral.
function levelClass(v) {
  if (!hasPct(v)) return 'gray'
  const p = pct(v)
  return p <= 15 ? 'crit' : p <= 40 ? 'amber' : 'green'
}
function levelBadge(v) { return { gray: 'offline', crit: 'critical', amber: 'idle', green: 'active' }[levelClass(v)] }
function levelText(v) {
  if (v.latest?.total_litres == null) return 'No reading'
  if (!v.tank_capacity_litres) return 'Reading'
  return { crit: 'Low', amber: 'Medium', green: 'Good' }[levelClass(v)]
}

const withReading = computed(() => vehicles.value.filter((v) => v.latest?.total_litres != null))
const totalLitres = computed(() => withReading.value.reduce((s, v) => s + Number(v.latest.total_litres), 0))
const avgPct = computed(() => {
  const w = vehicles.value.filter(hasPct)
  return w.length ? Math.round(w.reduce((s, v) => s + pct(v), 0) / w.length) : null
})
const lowCount = computed(() => vehicles.value.filter((v) => hasPct(v) && pct(v) <= 15).length)
const shown = computed(() => {
  const t = q.value.trim().toLowerCase()
  const list = vehicles.value.filter((v) => !t || [v.local_name, v.registration_number].some((x) => x?.toLowerCase().includes(t)))
  if (sort.value === 'name') return [...list].sort((a, b) => a.local_name.localeCompare(b.local_name, undefined, { numeric: true }))
  return [...list].sort((a, b) => (hasPct(b) - hasPct(a)) || (pct(a) - pct(b)))
})

const pager = usePaging(shown, 10, [q, sort])

async function load() {
  try { vehicles.value = await getVehicles() }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.fuel-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
.fuel-box { padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; color: inherit; transition: border-color var(--dur) var(--ease); }
.fuel-box:hover { border-color: var(--brand); text-decoration: none; }
.fb-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
.fb-name { font-weight: 700; font-size: 15px; color: var(--ink-strong); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.fb-reg { font-size: 12px; color: var(--muted); }
.fb-level { display: flex; align-items: baseline; gap: 4px; }
.fb-level b { font-size: 26px; font-weight: 800; letter-spacing: -.02em; color: var(--ink-strong); }
.fb-level > span { font-size: 13px; color: var(--muted); font-weight: 600; }
.fb-none { font-size: 14px !important; color: var(--muted); font-weight: 600; line-height: 36px; }
.fb-level .fb-pct { margin-left: auto; font-size: 13px; color: var(--text); font-weight: 700; }
.fb-foot { display: flex; justify-content: space-between; gap: 8px; font-size: 12px; color: var(--muted); }
.fv-pager { margin-top: 12px; }
.fv-pager :deep(.pager) { border-top: 0; }
.toolbar { margin-bottom: 12px; }
@media (max-width: 720px) {
  .fuel-grid { grid-template-columns: 1fr; gap: 8px; }
  .fuel-box { padding: 11px 14px; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px 10px; align-items: center; }
  .fb-top { grid-column: 1 / -1; }
  .fb-level { grid-row: 2; grid-column: 1; }
  .fb-level b { font-size: 18px; }
  .fb-none { line-height: 1.3; font-size: 13px !important; }
  .fb-level .fb-pct { margin-left: 8px; }
  .fb-foot { grid-row: 2; grid-column: 2; }
  .fb-foot > span:first-child { display: none; }
  .fuel-box .meter { grid-row: 3; grid-column: 1 / -1; }
  .toolbar .seg { flex: 1 1 auto; }
  .toolbar .seg button { flex: 1; }
}
</style>
