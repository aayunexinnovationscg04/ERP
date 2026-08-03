<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Systems</span>
      <h1 class="ico"><ScrollText :size="20" /> Audit &amp; Error Logs</h1>
    </div>
  </div>
  <p class="hint">Recent platform events. Illustrative sample feed — a persisted audit log store is not wired up yet.</p>

  <div class="chiprow">
    <div class="chip"><span class="chip-n num">{{ logs.length }}</span><span class="chip-l">Events shown</span></div>
    <div class="chip flag"><span class="chip-n num">{{ countByLevel.error }}</span><span class="chip-l">Errors</span></div>
    <div class="chip" style="border-top-color:var(--amber)"><span class="chip-n num">{{ countByLevel.warning }}</span><span class="chip-l">Warnings</span></div>
    <div class="chip" style="border-top-color:var(--info)"><span class="chip-n num">{{ countByLevel.info }}</span><span class="chip-l">Info</span></div>
  </div>

  <div class="row" style="margin-bottom:12px;gap:8px;flex-wrap:wrap">
    <button
      v-for="f in filters" :key="f.key" class="ghost" style="width:auto;padding:6px 12px;font-size:12.5px"
      :style="filter === f.key ? { background: 'var(--brand-soft)', color: 'var(--brand-bright)', borderColor: 'rgba(139,92,246,.35)' } : {}"
      @click="filter = f.key"
    >{{ f.label }}</button>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Timestamp</th><th>Level</th><th>Source</th><th>Message</th></tr></thead>
      <tbody v-if="!filtered.length"><tr><td colspan="4" class="muted" style="text-align:center;padding:22px">No events match this filter.</td></tr></tbody>
      <tbody v-else>
        <tr v-for="l in filtered" :key="l.id">
          <td class="muted num" style="white-space:nowrap">{{ l.ts }}</td>
          <td><span class="badge" :class="levelClass(l.level)">{{ l.level }}</span></td>
          <td>{{ l.source }}</td>
          <td class="muted">{{ l.message }}</td>
        </tr>
      </tbody>
    </table>
    <div class="table-foot">{{ filtered.length }} of {{ logs.length }} events</div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { ScrollText } from 'lucide-vue-next'

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
  const ts = new Date(Date.now() - minsAgo * 60000).toLocaleString()
  return {
    id: seed,
    ts,
    level,
    source: pick(sources, seed * 7 + 3),
    message: pick(messages[level], seed * 11 + 5),
    sortKey: minsAgo,
  }
}).sort((a, b) => a.sortKey - b.sortKey)

function levelClass(l) { return l === 'error' ? 'critical' : l === 'warning' ? 'warning' : 'info' }

const filters = [
  { key: 'all', label: 'All' },
  { key: 'info', label: 'Info' },
  { key: 'warning', label: 'Warning' },
  { key: 'error', label: 'Error' },
]
const filter = ref('all')
const filtered = computed(() => filter.value === 'all' ? logs : logs.filter((l) => l.level === filter.value))
const countByLevel = computed(() => ({
  info: logs.filter((l) => l.level === 'info').length,
  warning: logs.filter((l) => l.level === 'warning').length,
  error: logs.filter((l) => l.level === 'error').length,
}))
</script>
