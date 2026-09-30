<template>
  <PageHeader :icon="Cpu" title="Devices" description="Every Fuel Guard X telematics unit registered on the platform, with its latest check-in.">
    <span class="ph-meta" v-if="fetchedAt"><Clock :size="13" /> Updated {{ fmtTime(fetchedAt) }}</span>
    <button type="button" class="btn" :disabled="refreshing" @click="refresh"><RefreshCw :size="16" :class="{ spin: refreshing }" /> Refresh</button>
  </PageHeader>

  <div class="stats">
    <StatCard label="Devices" :value="fmt(devices.length)" :icon="Cpu" tone="navy" :loading="loading" />
    <StatCard label="Online" :value="fmt(onlineCount)" :icon="Wifi" tone="green" :loading="loading" :sub="loading ? '' : pct(onlineCount) + ' of fleet'" />
    <StatCard label="Offline" :value="fmt(devices.length - onlineCount)" :icon="WifiOff" :tone="devices.length - onlineCount ? 'red' : 'navy'" :loading="loading" />
    <StatCard label="Pending commands" :value="fmt(pendingTotal)" :icon="Send" :tone="pendingTotal ? 'amber' : 'navy'" :loading="loading" sub="Queued for delivery to devices" />
  </div>

  <div class="card">
    <div class="toolbar">
      <label class="input-icon">
        <Search :size="16" />
        <input v-model="q" class="input" type="search" placeholder="Search device ID, label, SIM or firmware" aria-label="Search devices" />
      </label>
      <div class="seg" role="group" aria-label="Filter by connection">
        <button v-for="f in filters" :key="f.key" type="button" :class="{ on: status === f.key }" @click="status = f.key">
          {{ f.label }} <span class="count">{{ f.count }}</span>
        </button>
      </div>
    </div>
    <div class="table-wrap">
      <table class="table stack">
        <thead>
          <tr><th>Device</th><th>Connection</th><th>Last seen</th><th>Firmware</th><th>SIM</th><th class="t-right">Pending cmds</th></tr>
        </thead>
        <TableSkeleton v-if="loading" :cols="6" :rows="7" />
        <tbody v-else-if="loadError">
          <tr class="table-empty"><td colspan="6"><EmptyState :icon="CircleAlert" title="Devices could not be loaded" text="Check your connection and try again."><button type="button" class="btn" @click="refresh">Try again</button></EmptyState></td></tr>
        </tbody>
        <tbody v-else-if="!filtered.length">
          <tr class="table-empty"><td colspan="6">
            <EmptyState v-if="!devices.length" :icon="Cpu" title="No devices registered" text="Devices appear here once they are provisioned for a company." />
            <EmptyState v-else :icon="Search" title="No matching devices" text="Try a different search or filter." />
          </td></tr>
        </tbody>
        <tbody v-else>
          <tr v-for="d in pagedRows" :key="d.id">
            <td class="cell-head">
              <div class="cell-entity">
                <span class="entity-mark"><Cpu :size="16" /></span>
                <div><div class="t-primary mono">{{ d.device_id }}</div><div v-if="d.label" class="t-secondary">{{ d.label }}</div></div>
              </div>
            </td>
            <td data-label="Connection"><span class="badge" :class="d.online ? 'success' : 'neutral'"><span class="bdot"></span>{{ d.online ? 'Online' : 'Offline' }}</span></td>
            <td data-label="Last seen" class="nowrap" :title="fmtDateTime(d.last_seen)">{{ relTime(d.last_seen) }}</td>
            <td data-label="Firmware" class="mono muted">{{ d.firmware_version || '—' }}</td>
            <td data-label="SIM" class="mono muted">{{ d.sim_number || '—' }}</td>
            <td data-label="Pending cmds" class="t-right num">
              <span v-if="d.pending_commands" class="badge warning">{{ d.pending_commands }}</span>
              <span v-else class="muted">0</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Cpu, Wifi, WifiOff, Send, Search, Clock, RefreshCw, CircleAlert } from 'lucide-vue-next'
import { getDevices } from '../api'
import { fmt, fmtTime, fmtDateTime, relTime } from '../format'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import TableSkeleton from '../components/TableSkeleton.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const devices = ref([])
const loading = ref(true)
const refreshing = ref(false)
const loadError = ref(false)
const fetchedAt = ref(null)
const q = ref('')
const status = ref('all')

const onlineCount = computed(() => devices.value.filter((d) => d.online).length)
const pendingTotal = computed(() => devices.value.reduce((s, d) => s + (d.pending_commands || 0), 0))
const pct = (n) => (devices.value.length ? Math.round((n / devices.value.length) * 100) + '%' : '0%')
const filters = computed(() => [
  { key: 'all', label: 'All', count: devices.value.length },
  { key: 'online', label: 'Online', count: onlineCount.value },
  { key: 'offline', label: 'Offline', count: devices.value.length - onlineCount.value },
])
const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  return devices.value
    .filter((d) => status.value === 'all' || (status.value === 'online') === !!d.online)
    .filter((d) => !term || [d.device_id, d.label, d.sim_number, d.firmware_version].some((f) => (f || '').toLowerCase().includes(term)))
    .sort((a, b) => (a.online === b.online ? a.device_id.localeCompare(b.device_id) : a.online ? 1 : -1))
})

async function load() {
  try {
    devices.value = await getDevices()
    fetchedAt.value = new Date()
    loadError.value = false
  } catch (e) {
    loadError.value = !devices.value.length
  } finally { loading.value = false }
}
async function refresh() { refreshing.value = true; await load(); refreshing.value = false }
onMounted(load)

// pagination (resets to page 1 when search/filters change)
const pager = usePaging(filtered)
const pagedRows = pager.rows
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
.spin { animation: spin .8s linear infinite; }
</style>
