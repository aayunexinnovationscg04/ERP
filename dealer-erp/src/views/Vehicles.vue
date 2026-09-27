<template>
  <PageHeader title="Vehicles" description="Every vehicle in your fleet with its live status, fuel and last telemetry.">
    <router-link to="/locations" class="btn"><LocateFixed :size="16" /> View on map</router-link>
  </PageHeader>

  <div v-if="loading" class="kpis"><div class="skel sk-chip" v-for="n in 4" :key="n"></div></div>
  <div v-else class="kpis">
    <StatTile label="Total fleet" :value="vehicles.length" :icon="Truck" tone="navy" />
    <StatTile label="Active now" :value="activeCount" :icon="Navigation" tone="green" />
    <StatTile label="Idle / maintenance" :value="idleCount" :icon="PauseCircle" tone="amber" />
    <StatTile label="Avg fuel level" :value="avgFuelPct == null ? '—' : avgFuelPct" :unit="avgFuelPct == null ? '' : '%'" :icon="Fuel" tone="blue"
      :sub="avgFuelPct == null ? 'No fuel readings yet' : 'Across vehicles with a tank size set'" />
  </div>

  <div class="card flush">
    <div class="card-head" v-if="loading || vehicles.length">
      <div class="toolbar" style="margin:0;flex:1">
        <label class="search">
          <Search :size="16" />
          <input v-model="q" type="search" placeholder="Search name, registration, pilot…" aria-label="Search vehicles" />
        </label>
        <div class="chips">
          <button v-for="f in FILTERS" :key="f.key" type="button" class="chip" :class="{ on: statusFilter === f.key }"
                  @click="statusFilter = f.key">
            {{ f.label }} <span class="chip-count">{{ f.key ? (statusCounts[f.key] || 0) : vehicles.length }}</span>
          </button>
        </div>
      </div>
      <button type="button" class="sm" @click="cyclePriority" :title="priorityTitle">
        <component :is="priorityIcon" :size="15" /> {{ priorityLabel }}
      </button>
    </div>

    <div v-if="loading" class="card-body"><div class="skel sk-row" v-for="n in 6" :key="n"></div></div>

    <EmptyState v-else-if="!vehicles.length" :icon="Truck" title="No vehicles yet"
      text="Vehicles appear here once your administrator links a Fuel Guard X device to your company." />
    <EmptyState v-else-if="!shown.length" compact :icon="SearchX" title="No matching vehicles"
      text="Try a different search or status filter.">
      <button type="button" class="sm" @click="q = ''; statusFilter = ''">Clear filters</button>
    </EmptyState>

    <template v-else>
      <!-- desktop / tablet table -->
      <div class="table-wrap hide-sm">
        <table>
          <thead>
            <tr>
              <th>Vehicle</th><th>Status</th><th>Pilot</th><th class="num">Fuel</th>
              <th class="hide-md">Device</th><th>Last update</th><th style="width:48px"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in shown" :key="v.id" class="clickable" @click="$router.push(`/vehicles/${v.id}`)">
              <td>
                <div class="cell-with-icon">
                  <span class="icon-chip" :class="statusChip(v.status)"><component :is="statusIcon(v.status)" :size="16" /></span>
                  <div style="min-width:0">
                    <div class="name-line">
                      <span class="cell-main">{{ v.local_name }}</span>
                      <button v-if="canWrite" type="button" class="ghost icon-btn sm rename" title="Rename" aria-label="Rename vehicle" @click.stop="renaming = v">
                        <Pencil :size="13" />
                      </button>
                    </div>
                    <div class="cell-sub">{{ v.registration_number }}<span v-if="v.make || v.model" class="hide-md"> · {{ [v.make, v.model].filter(Boolean).join(' ') }}</span></div>
                  </div>
                </div>
              </td>
              <td><span class="badge" :class="v.status">{{ v.status }}</span></td>
              <td>{{ v.active_pilot?.name || v.pilot_name || '—' }}</td>
              <td class="num">
                <template v-if="v.latest?.total_litres != null">{{ fmt(v.latest.total_litres) }} L</template>
                <span v-else class="muted">—</span>
              </td>
              <td class="muted hide-md">{{ v.device_id || '—' }}</td>
              <td class="nowrap"><span class="ico"><span class="dot" :class="freshness(v)"></span>{{ ago(v.latest?.received_at) }}</span></td>
              <td><router-link class="row-link" :to="`/vehicles/${v.id}`" title="Open vehicle" @click.stop><ChevronRight :size="17" /></router-link></td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- phone list -->
      <div class="list show-sm">
        <div v-for="v in shown" :key="v.id" class="list-row clickable" @click="$router.push(`/vehicles/${v.id}`)">
          <span class="icon-chip" :class="statusChip(v.status)"><component :is="statusIcon(v.status)" :size="16" /></span>
          <span class="grow">
            <div class="title">{{ v.local_name }}</div>
            <div class="sub ico" style="gap:6px"><span class="dot" :class="freshness(v)"></span>{{ v.registration_number }} · {{ ago(v.latest?.received_at) }}
              <template v-if="v.latest?.total_litres != null"> · {{ fmt(v.latest.total_litres) }} L</template></div>
          </span>
          <span class="badge" :class="v.status">{{ v.status }}</span>
          <button v-if="canWrite" type="button" class="ghost icon-btn" aria-label="Rename vehicle" @click.stop="renaming = v"><Pencil :size="15" /></button>
        </div>
      </div>
    </template>
  </div>

  <RenameVehicleModal v-if="renaming" :vehicle="renaming" @close="renaming = null" @saved="onRenamed" />
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import {
  ArrowDownAZ, ArrowUpNarrowWide, ChevronRight, Fuel, LocateFixed, Navigation, PauseCircle, Pencil, Search, SearchX,
  Truck, Wrench, WifiOff,
} from 'lucide-vue-next'
import { getVehicles } from '../api'
import { auth } from '../auth'
import { freshness, ago, fmt } from '../util'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import RenameVehicleModal from '../components/RenameVehicleModal.vue'

const canWrite = computed(() => auth.user?.may_write !== false)
const STATUS_ICON = { active: Navigation, idle: PauseCircle, maintenance: Wrench, offline: WifiOff }
const STATUS_CHIP = { active: 'green', idle: 'amber', maintenance: 'amber', offline: 'gray' }
function statusIcon(status) { return STATUS_ICON[status] || Truck }
function statusChip(status) { return STATUS_CHIP[status] || 'gray' }

const FILTERS = [
  { key: '', label: 'All' },
  { key: 'active', label: 'Active' },
  { key: 'idle', label: 'Idle' },
  { key: 'maintenance', label: 'Maintenance' },
  { key: 'offline', label: 'Offline' },
]

// Which status the API pins to the top (?priority_status=). null = A–Z.
const PRIORITY_CYCLE = [null, 'active', 'offline', 'idle', 'maintenance']
const PRIORITY_LABELS = { null: 'Sort: A–Z', active: 'Active first', offline: 'Offline first', idle: 'Idle first', maintenance: 'Maintenance first' }

const vehicles = ref([])
const loading = ref(true)
const priorityIndex = ref(0)
const renaming = ref(null)
const q = ref('')
const statusFilter = ref('')
let timer

const priorityStatus = computed(() => PRIORITY_CYCLE[priorityIndex.value])
const priorityIcon = computed(() => (priorityStatus.value ? ArrowUpNarrowWide : ArrowDownAZ))
const priorityLabel = computed(() => PRIORITY_LABELS[priorityStatus.value])
const priorityTitle = computed(() => 'Change sort order (currently: ' + priorityLabel.value + ')')

const statusCounts = computed(() => {
  const c = {}
  vehicles.value.forEach((v) => { c[v.status] = (c[v.status] || 0) + 1 })
  return c
})
const shown = computed(() => {
  const term = q.value.trim().toLowerCase()
  return vehicles.value.filter((v) => {
    if (statusFilter.value && v.status !== statusFilter.value) return false
    if (!term) return true
    return [v.local_name, v.registration_number, v.device_id, v.active_pilot?.name, v.pilot_name, v.make, v.model]
      .some((x) => x && String(x).toLowerCase().includes(term))
  })
})

const activeCount = computed(() => vehicles.value.filter((v) => v.status === 'active').length)
const idleCount = computed(() => vehicles.value.filter((v) => v.status === 'idle' || v.status === 'maintenance').length)
const avgFuelPct = computed(() => {
  const withData = vehicles.value.filter((v) => v.tank_capacity_litres && v.latest?.total_litres != null)
  if (!withData.length) return null
  const pct = withData.reduce((s, v) => s + v.latest.total_litres / v.tank_capacity_litres, 0) / withData.length
  return Math.round(pct * 100)
})

function cyclePriority() { priorityIndex.value = (priorityIndex.value + 1) % PRIORITY_CYCLE.length }

function onRenamed(name) {
  // Look up by id in case the 15s poll replaced the array while the modal was open.
  const veh = vehicles.value.find((x) => x.id === renaming.value.id)
  if (veh) veh.local_name = name
  renaming.value = null
}

async function load() {
  try {
    const params = priorityStatus.value ? { priority_status: priorityStatus.value } : {}
    vehicles.value = await getVehicles(params)
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}

watch(priorityStatus, load)
onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.name-line { display: flex; align-items: center; gap: 4px; }
.rename { opacity: 0; color: var(--muted); }
tr:hover .rename, .rename:focus-visible { opacity: 1; }
@media (hover: none) { .rename { opacity: 1; } }
</style>
