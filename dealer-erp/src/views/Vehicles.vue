<template>
  <div class="topbar">
    <h1>Vehicles</h1>
    <span class="muted">{{ vehicles.length }} vehicle(s)</span>
  </div>

  <div v-if="loading" class="kpis">
    <div class="skel sk-chip" v-for="n in 4" :key="n"></div>
  </div>
  <div v-else class="kpis">
    <motion.div class="card kpi" :while-hover="{ y: -2 }">
      <Truck :size="16" class="ic" /><div class="n">{{ vehicles.length }}</div><div class="l">Total fleet</div>
    </motion.div>
    <motion.div class="card kpi hero" :while-hover="{ y: -2 }">
      <Activity :size="16" class="ic" /><div class="n">{{ activeCount }}</div><div class="l">Active now</div>
    </motion.div>
    <motion.div class="card kpi" :while-hover="{ y: -2 }">
      <PauseCircle :size="16" class="ic" /><div class="n">{{ idleCount }}</div><div class="l">Idle / maint.</div>
    </motion.div>
    <motion.div class="card kpi" :while-hover="{ y: -2 }">
      <Fuel :size="16" class="ic" /><div class="n">{{ avgFuelPct == null ? '—' : avgFuelPct + '%' }}</div><div class="l">Avg fuel level</div>
    </motion.div>
  </div>

  <div v-if="loading" style="padding:2px 0">
    <div class="skel sk-row" v-for="n in 6" :key="n"></div>
  </div>

  <div v-else class="card" style="padding:6px 0">
    <table>
      <thead>
        <tr>
          <th>Truck</th>
          <th>
            <button type="button" class="status-sort" @click="cyclePriority" :title="priorityTitle">
              Status <component :is="priorityIcon" :size="14" />
            </button>
          </th>
          <th class="col-optional">Fuel (L)</th>
          <th class="col-optional">Device</th>
          <th class="col-optional">Last seen</th>
          <th class="col-actions"></th>
        </tr>
      </thead>
      <tbody>
        <motion.tr v-for="(v, i) in vehicles" :key="v.id"
          :initial="{ opacity: 0, y: 6 }" :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: .22, delay: Math.min(i, 12) * .025, ease: [.4, 0, .2, 1] }">
          <td>
            <span class="dot" :class="freshness(v)"></span>
            <button type="button" class="local-name-btn" @click="renaming = v" title="Rename">
              {{ v.local_name }} <Pencil :size="12" class="pencil" />
            </button>
            <div class="muted" style="font-size:12px">{{ v.registration_number }}</div>
          </td>
          <td><span class="badge" :class="v.status">{{ v.status }}</span></td>
          <td class="col-optional">{{ fmt(v.latest?.total_litres) }}</td>
          <td class="col-optional muted">{{ v.device_id || '—' }}</td>
          <td class="col-optional muted">{{ ago(v.latest?.received_at) }}</td>
          <td class="col-actions">
            <router-link class="row-action" :to="`/vehicles/${v.id}`" title="Open vehicle profile">
              <ChevronRight :size="17" />
            </router-link>
          </td>
        </motion.tr>
        <tr v-if="!vehicles.length"><td colspan="6" class="muted" style="padding:16px">No vehicles yet.</td></tr>
      </tbody>
    </table>
  </div>

  <RenameVehicleModal v-if="renaming" :vehicle="renaming" @close="renaming = null"
                       @saved="onRenamed" />
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { Activity, ArrowDownAZ, ChevronRight, Fuel, PauseCircle, Pencil, Truck } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { getVehicles } from '../api'
import { freshness, ago, fmt } from '../util'
import RenameVehicleModal from '../components/RenameVehicleModal.vue'

// Which status is pinned to the top of the table. null = default (alphabetical
// by registration number). The API does the actual sorting (?priority_status=);
// this only remembers which arrow state we're on and what to ask for next.
const PRIORITY_CYCLE = [null, 'active', 'offline', 'idle', 'maintenance']
const PRIORITY_TITLES = {
  null: 'Sort: alphabetical — click to prioritise Active',
  active: 'Prioritising Active — click to prioritise Inactive',
  offline: 'Prioritising Inactive — click to prioritise Idle',
  idle: 'Prioritising Idle — click to prioritise Maintenance',
  maintenance: 'Prioritising Maintenance — click to reset',
}

const vehicles = ref([])
const loading = ref(true)
const priorityIndex = ref(0)
const renaming = ref(null)
let timer

const priorityStatus = computed(() => PRIORITY_CYCLE[priorityIndex.value])
const priorityIcon = computed(() => (priorityStatus.value ? ChevronRight : ArrowDownAZ))
const priorityTitle = computed(() => PRIORITY_TITLES[priorityStatus.value])

// Lightweight fleet-at-a-glance tiles, derived entirely from the vehicle list
// already being polled every 15s — no extra network round-trip needed.
const activeCount = computed(() => vehicles.value.filter((v) => v.status === 'active').length)
const idleCount = computed(() => vehicles.value.filter((v) => v.status === 'idle' || v.status === 'maintenance').length)
const avgFuelPct = computed(() => {
  const withData = vehicles.value.filter((v) => v.tank_capacity_litres && v.latest?.total_litres != null)
  if (!withData.length) return null
  const pct = withData.reduce((s, v) => s + v.latest.total_litres / v.tank_capacity_litres, 0) / withData.length
  return Math.round(pct * 100)
})

function cyclePriority() {
  priorityIndex.value = (priorityIndex.value + 1) % PRIORITY_CYCLE.length
}

function onRenamed(name) {
  // Look up by id (not the captured `renaming` reference) in case the 15s
  // poll swapped `vehicles` for a fresh array while the modal was open —
  // mutating a stale object would silently not show up until the next poll.
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
.status-sort {
  border: none; background: none; padding: 0; font: inherit; font-weight: 700; color: inherit;
  display: inline-flex; align-items: center; gap: 4px; cursor: pointer;
}
.status-sort:hover { color: var(--brand); }

.local-name-btn {
  border: none; background: none; padding: 4px 0; font: inherit; font-weight: 600; color: var(--text);
  display: inline-flex; align-items: center; gap: 6px;
}
.local-name-btn .pencil { color: var(--muted); opacity: 0; transition: opacity var(--dur) var(--ease); }
.local-name-btn:hover .pencil { opacity: 1; }
.local-name-btn:hover { color: var(--brand); }

.col-actions { width: 40px; text-align: right; }
.row-action {
  display: inline-flex; align-items: center; justify-content: center;
  width: 30px; height: 30px; border-radius: var(--radius-sm); color: var(--muted);
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}
.row-action:hover { background: var(--surface-2); color: var(--brand); }

@media (max-width: 720px) {
  .col-optional { display: none; }
  /* Only 4 columns remain visible; override the app-wide safety-net min-width
     (560px, sized for wider tables) so this table fits without side-scroll. */
  table { min-width: 0; }
}
</style>
