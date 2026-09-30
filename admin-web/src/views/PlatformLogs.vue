<template>
  <PageHeader :icon="ScrollText" title="Audit & Error Logs" description="Platform events from ingest, authentication, the database and background workers." />

  <div class="notice info">
    <FlaskConical :size="16" />
    <span><strong>Sample data</strong> <span class="muted">· live audit log not connected yet</span></span>
  </div>

  <div class="stats">
    <StatCard label="Events shown" :value="logs.length" :icon="List" tone="navy" />
    <StatCard label="Errors" :value="countByLevel.error" :icon="CircleAlert" :tone="countByLevel.error ? 'red' : 'navy'" />
    <StatCard label="Warnings" :value="countByLevel.warning" :icon="TriangleAlert" :tone="countByLevel.warning ? 'amber' : 'navy'" />
    <StatCard label="Info" :value="countByLevel.info" :icon="Info" tone="info" />
  </div>

  <div class="card">
    <div class="toolbar">
      <label class="input-icon">
        <Search :size="16" />
        <input v-model="q" class="input" type="search" placeholder="Search message or source" aria-label="Search events" />
      </label>
      <div class="seg" role="group" aria-label="Filter by level">
        <button type="button" :class="{ on: filter === 'all' }" @click="filter = 'all'">All <span class="count">{{ logs.length }}</span></button>
        <button type="button" :class="{ on: filter === 'error' }" @click="filter = 'error'">Errors <span class="count">{{ countByLevel.error }}</span></button>
        <button type="button" :class="{ on: filter === 'warning' }" @click="filter = 'warning'">Warnings <span class="count">{{ countByLevel.warning }}</span></button>
        <button type="button" :class="{ on: filter === 'info' }" @click="filter = 'info'">Info <span class="count">{{ countByLevel.info }}</span></button>
      </div>
    </div>
    <div class="table-wrap">
      <table class="table stack">
        <thead><tr><th>Time</th><th>Level</th><th>Source</th><th>Message</th></tr></thead>
        <tbody v-if="!filtered.length">
          <tr class="table-empty"><td colspan="4"><EmptyState :icon="Search" title="No matching events" text="Try a different level or search." /></td></tr>
        </tbody>
        <tbody v-else>
          <tr v-for="l in pagedRows" :key="l.id">
            <td data-label="Time" class="nowrap muted num">{{ l.ts }}</td>
            <td data-label="Level"><span class="badge lvl" :class="levelClass(l.level)"><span class="bdot"></span>{{ l.level }}</span></td>
            <td data-label="Source" class="mono nowrap">{{ l.source }}</td>
            <td data-label="Message" class="cell-full msg">{{ l.message }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ScrollText, FlaskConical, Search, CircleAlert, TriangleAlert, Info, List } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const sources = ['ingest', 'auth', 'database', 'admin-api', 'fleet-sync', 'alerts-engine']
const messages = {
  info: [
    'Telemetry batch processed successfully',
    'Scheduled cache refresh completed',
    'User session established',
    'Device heartbeat received',
    'Nightly aggregation job finished',
  ],
  warning: [
    'Ingest latency exceeded 2s for device esp32-014',
    'Retry attempted after transient DB timeout',
    'Device esp32-027 telemetry gap > 10 min',
    'JWT refresh token nearing expiry threshold',
    'Company quota approaching configured limit',
  ],
  error: [
    'Failed to persist telemetry payload — malformed JSON',
    'Database connection pool exhausted',
    'Unhandled exception in alerts-engine worker',
    'Device authentication rejected — unknown device_id',
    'Backfill job aborted after 3 retries',
  ],
}
const levels = ['info', 'info', 'info', 'warning', 'warning', 'error']

function seeded(seed) {
  const x = Math.sin(seed * 21.17 + 3.71) * 71829.19
  return x - Math.floor(x)
}
function pick(arr, seed) { return arr[Math.floor(seeded(seed) * arr.length)] }

const logs = Array.from({ length: 26 }, (_, i) => {
  const seed = i + 1
  const level = pick(levels, seed * 2 + 1)
  const minsAgo = Math.floor(seeded(seed * 5 + 2) * 2880)
  const ts = new Date(Date.now() - minsAgo * 60000).toLocaleString(undefined, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
  return {
    id: seed,
    ts,
    level,
    source: pick(sources, seed * 7 + 3),
    message: pick(messages[level], seed * 11 + 5),
    sortKey: minsAgo,
  }
}).sort((a, b) => a.sortKey - b.sortKey)

function levelClass(l) { return l === 'error' ? 'danger' : l === 'warning' ? 'warning' : 'info' }

const filter = ref('all')
const q = ref('')
const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  return logs
    .filter((l) => filter.value === 'all' || l.level === filter.value)
    .filter((l) => !term || l.message.toLowerCase().includes(term) || l.source.includes(term))
})
const countByLevel = computed(() => ({
  info: logs.filter((l) => l.level === 'info').length,
  warning: logs.filter((l) => l.level === 'warning').length,
  error: logs.filter((l) => l.level === 'error').length,
}))

// pagination (resets to page 1 when search/filters change)
const pager = usePaging(filtered)
const pagedRows = pager.rows
</script>

<style scoped>
.lvl { text-transform: capitalize; }
.msg { min-width: 260px; }
@media (max-width: 720px) { .msg { min-width: 0; } }
</style>
