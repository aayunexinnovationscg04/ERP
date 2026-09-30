<!--
  Device data: every device reporting in through the receiver dashboard (which
  forwards each packet to the ERP), and the packets it sends. Admin only.
-->
<template>
  <PageHeader>
    <span class="ph-meta" v-if="fetchedAt"><Clock :size="13" /> Updated {{ fmtTime(fetchedAt) }}</span>
    <button type="button" class="btn" :disabled="refreshing" @click="load(true)"><RefreshCw :size="16" :class="{ spin: refreshing }" /> Refresh</button>
  </PageHeader>

  <div class="stats">
    <StatCard label="Reporting today" :value="fmt(reporting)" :icon="RadioTower" tone="navy" :loading="loading" />
    <StatCard label="Packets today" :value="fmt(packets24)" :icon="Activity" tone="info" :loading="loading" />
    <StatCard label="Online now" :value="fmt(onlineCount)" :icon="Wifi" tone="green" :loading="loading" />
    <StatCard label="Unassigned" :value="fmt(unassigned)" :icon="CircleDashed" :tone="unassigned ? 'amber' : 'navy'" :loading="loading" />
  </div>

  <div class="card">
    <div class="toolbar">
      <label class="input-icon">
        <Search :size="16" />
        <input v-model="q" class="input" type="search" placeholder="Search device, company or vehicle" aria-label="Search devices" />
      </label>
      <div class="seg" role="group" aria-label="Filter devices">
        <button v-for="f in filters" :key="f.key" type="button" :class="{ on: show === f.key }" @click="show = f.key">
          {{ f.label }} <span class="count">{{ f.count }}</span>
        </button>
      </div>
    </div>
    <div class="table-wrap">
      <table class="table stack">
        <thead>
          <tr><th>Device</th><th>Assigned to</th><th>Status</th><th>Last packet</th><th class="t-right">Packets 24 h</th><th>Latest reading</th><th class="t-right">Data</th></tr>
        </thead>
        <TableSkeleton v-if="loading" :cols="7" :rows="7" />
        <tbody v-else-if="loadError">
          <tr class="table-empty"><td colspan="7"><EmptyState :icon="CircleAlert" title="Device data could not be loaded" text="Check your connection and try again."><button type="button" class="btn" @click="load(true)">Try again</button></EmptyState></td></tr>
        </tbody>
        <tbody v-else-if="!filtered.length">
          <tr class="table-empty"><td colspan="7">
            <EmptyState v-if="!devices.length" :icon="RadioTower" title="No devices have reported yet" text="Devices appear here after their first packet reaches the receiver." />
            <EmptyState v-else :icon="Search" title="No matching devices" text="Try a different search or filter." />
          </td></tr>
        </tbody>
        <tbody v-else>
          <tr v-for="d in pagedRows" :key="d.id">
            <td class="cell-head">
              <div class="t-primary mono">{{ d.device_id }}</div>
              <div class="t-secondary">{{ d.label || (d.last_ip ? 'IP ' + d.last_ip : '—') }}</div>
            </td>
            <td data-label="Assigned to">
              <template v-if="d.company">
                <div>{{ d.company }}</div>
                <div class="t-secondary mono">{{ d.vehicle || 'No vehicle' }}</div>
              </template>
              <span v-else class="badge warning">Not assigned</span>
            </td>
            <td data-label="Status"><span class="status-dot" :class="d.online ? 'green' : ''">{{ d.online ? 'Online' : 'Offline' }}</span></td>
            <td data-label="Last packet" :title="d.last_seen ? fmtDateTime(d.last_seen) : ''">{{ d.last_seen ? relTime(d.last_seen) : 'Never' }}</td>
            <td data-label="Packets 24 h" class="t-right num">{{ fmt(d.packets_24h) }} <span class="muted">/ {{ fmt(d.packets_total) }}</span></td>
            <td data-label="Latest reading">
              <span v-if="d.latest" class="reading">{{ reading(d.latest) }}</span>
              <span v-else class="muted">—</span>
            </td>
            <td data-label="Data" class="t-right">
              <button type="button" class="btn btn-sm" :disabled="!d.packets_total" @click="openPackets(d)">
                <ListTree :size="14" /> Packets
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>

  <Modal :open="!!active" :title="active ? active.device_id : ''" :description="active ? packetsTitle : ''" size="lg" @close="active = null">
    <div v-if="packetsLoading" class="skel skel-line" style="height:120px"></div>
    <p v-else-if="packetsError" class="form-error"><CircleAlert :size="16" /> {{ packetsError }}</p>
    <ul v-else class="packets">
      <li v-for="p in packets" :key="p.id" class="packet">
        <button type="button" class="packet-head" :aria-expanded="open === p.id" @click="open = open === p.id ? null : p.id">
          <span class="packet-time">{{ fmtDateTime(p.received_at) }}</span>
          <span class="packet-sum">{{ reading(p) }}</span>
          <ChevronDown :size="16" class="packet-chev" />
        </button>
        <div v-if="open === p.id" class="packet-body">
          <dl class="packet-grid">
            <div><dt>Position</dt><dd class="mono">{{ p.latitude != null ? `${p.latitude.toFixed(5)}, ${p.longitude.toFixed(5)}` : '—' }}</dd></div>
            <div><dt>Speed</dt><dd>{{ p.speed_kmph != null ? p.speed_kmph + ' km/h' : '—' }}</dd></div>
            <div><dt>Satellites</dt><dd>{{ p.satellites ?? '—' }}</dd></div>
            <div><dt>Fuel total</dt><dd>{{ p.total_litres != null ? p.total_litres + ' L' : '—' }}</dd></div>
            <div><dt>Flow</dt><dd>{{ p.flow_rate_lpm != null ? p.flow_rate_lpm + ' L/min' : '—' }}</dd></div>
            <div><dt>Lock</dt><dd>{{ p.lock_active == null ? '—' : p.lock_active ? 'Locked' : 'Open' }}</dd></div>
            <div><dt>Signal</dt><dd>{{ p.gsm_signal ?? '—' }}</dd></div>
            <div><dt>Receiver seq</dt><dd class="mono">{{ p.seq ?? '—' }}</dd></div>
          </dl>
          <pre class="packet-raw">{{ JSON.stringify(p.raw, null, 2) }}</pre>
        </div>
      </li>
    </ul>
  </Modal>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import {
  Activity, ChevronDown, CircleAlert, CircleDashed, Clock, ListTree, RadioTower, RefreshCw, Search, Wifi,
} from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import TableSkeleton from '../components/TableSkeleton.vue'
import Modal from '../components/Modal.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { getIngestDevices, getIngestPackets } from '../api'
import { fmt, fmtDateTime, fmtTime, relTime } from '../format'

const devices = ref([])
const loading = ref(true)
const refreshing = ref(false)
const loadError = ref(false)
const fetchedAt = ref(null)

async function load(manual = false) {
  if (manual) refreshing.value = true
  try {
    devices.value = await getIngestDevices()
    loadError.value = false
    fetchedAt.value = new Date()
  } catch (e) {
    if (!devices.value.length) loadError.value = true
  } finally {
    loading.value = false
    refreshing.value = false
  }
}
let timer = null
onMounted(() => { load(); timer = setInterval(load, 15000) })   // live-ish: every 15 s
onBeforeUnmount(() => clearInterval(timer))

const reporting = computed(() => devices.value.filter((d) => d.packets_24h > 0).length)
const packets24 = computed(() => devices.value.reduce((n, d) => n + d.packets_24h, 0))
const onlineCount = computed(() => devices.value.filter((d) => d.online).length)
const unassigned = computed(() => devices.value.filter((d) => !d.company).length)

const q = ref('')
const show = ref('all')
const filters = computed(() => [
  { key: 'all', label: 'All', count: devices.value.length },
  { key: 'online', label: 'Online', count: onlineCount.value },
  { key: 'offline', label: 'Offline', count: devices.value.length - onlineCount.value },
  { key: 'unassigned', label: 'Unassigned', count: unassigned.value },
])
const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  return devices.value.filter((d) => {
    if (show.value === 'online' && !d.online) return false
    if (show.value === 'offline' && d.online) return false
    if (show.value === 'unassigned' && d.company) return false
    if (!term) return true
    return [d.device_id, d.label, d.company, d.vehicle, d.last_ip].some((v) => v && String(v).toLowerCase().includes(term))
  })
})
const pager = usePaging(filtered)
const pagedRows = pager.rows

// one-line summary of a packet
function reading(p) {
  const bits = []
  if (p.speed_kmph != null) bits.push(`${Math.round(p.speed_kmph)} km/h`)
  if (p.satellites != null) bits.push(`${p.satellites} sats`)
  if (p.total_litres != null) bits.push(`${p.total_litres} L`)
  if (p.lock_active != null) bits.push(p.lock_active ? 'locked' : 'lock open')
  return bits.length ? bits.join(' · ') : 'No readings in packet'
}

// ---- packets dialog ----
const active = ref(null)
const packets = ref([])
const packetsLoading = ref(false)
const packetsError = ref('')
const open = ref(null)
const packetsTitle = computed(() => `Last ${packets.value.length || ''} packets${active.value?.company ? ' · ' + active.value.company : ''}`)
async function openPackets(d) {
  active.value = d; packets.value = []; packetsError.value = ''; open.value = null; packetsLoading.value = true
  try {
    packets.value = await getIngestPackets(d.id, 50)
    open.value = packets.value[0]?.id ?? null
  } catch (e) {
    packetsError.value = 'Packets could not be loaded.'
  } finally {
    packetsLoading.value = false
  }
}
</script>

<style scoped>
.reading { font-size: .8125rem; white-space: nowrap; }
.packets { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.packet { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
.packet-head {
  width: 100%; display: flex; align-items: center; gap: 12px; padding: 10px 12px; min-height: 44px;
  border: 0; background: var(--surface); color: var(--text); font: inherit; text-align: left; cursor: pointer;
  box-shadow: none; transform: none;
}
.packet-head:hover { background: var(--surface-2); transform: none; }
.packet-time { flex: none; font-size: .8125rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.packet-sum { flex: 1; min-width: 0; font-size: .8125rem; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.packet-chev { flex: none; color: var(--muted); transition: transform var(--dur) var(--ease); }
.packet-head[aria-expanded="true"] .packet-chev { transform: rotate(180deg); }
.packet-body { padding: 12px; border-top: 1px solid var(--border); background: var(--surface-2); }
.packet-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px 14px; margin: 0 0 12px; }
.packet-grid dt { font-size: .68rem; font-weight: 700; letter-spacing: .05em; text-transform: uppercase; color: var(--muted); }
.packet-grid dd { margin: 2px 0 0; font-size: .8125rem; overflow-wrap: anywhere; }
.packet-raw {
  margin: 0; padding: 10px 12px; max-height: 220px; overflow: auto; border-radius: 8px;
  background: var(--navy-900); color: #D6E0EC; font-family: var(--font-mono); font-size: .75rem; line-height: 1.5;
}
@media (max-width: 720px) {
  .packet-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .packet-head { flex-wrap: wrap; row-gap: 2px; }
  .packet-sum { flex-basis: 100%; }
  .packet-chev { position: absolute; right: 12px; }
  .packet-head { position: relative; padding-right: 36px; }
}
</style>
