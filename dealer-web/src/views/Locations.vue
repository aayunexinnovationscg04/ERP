<template>
  <div v-if="loading" class="lm-layout">
    <div class="skel sk-map lm-map-skel"></div>
    <div class="card card-body"><div class="skel sk-row" v-for="n in 6" :key="n"></div></div>
  </div>

  <div v-else-if="!vehicles.length" class="card">
    <EmptyState :icon="LocateFixed" title="No vehicles to show" />
  </div>

  <div v-else class="lm-layout">
    <div class="card flush lm-map-card">
      <div class="card-head">
        <div class="card-head-title"><LocateFixed :size="17" /><div><h2>{{ focused ? focused.local_name : 'All vehicles' }}</h2>
          <div v-if="focused" class="card-sub">{{ focused.registration_number + ' · ' + ago(focused.latest?.received_at) }}</div></div></div>
        <button v-if="focusId != null" type="button" class="sm" @click="focusId = null"><Maximize2 :size="14" /> Show all</button>
        <div v-else class="map-legend">
          <span><i class="swatch" style="background:#059669"></i>Active</span>
          <span><i class="swatch" style="background:#D97706"></i>Idle</span>
          <span><i class="swatch" style="background:#64748B"></i>Offline</span>
        </div>
      </div>
      <FleetMap :markers="markers" :track="focusTrack" :focus="focusId" map-class="lm-map" @select="(id) => (focusId = id)" />
      <div v-if="focused?.latest?.has_gps_fix" class="coord-row">
        <div><span class="k">Latitude</span><b class="num">{{ Number(focused.latest.latitude).toFixed(6) }}</b></div>
        <div><span class="k">Longitude</span><b class="num">{{ Number(focused.latest.longitude).toFixed(6) }}</b></div>
        <div><span class="k">Speed</span><b class="num">{{ fmt(focused.latest.speed_kmph, 0) }} km/h</b></div>
        <router-link :to="`/vehicles/${focused.id}`" class="btn sm" style="margin-left:auto">Open vehicle <ChevronRight :size="14" /></router-link>
      </div>
    </div>

    <div class="card flush lm-list-card">
      <div class="card-head">
        <label class="search" style="max-width:none">
          <Search :size="16" />
          <input v-model="q" type="search" placeholder="Find a vehicle…" aria-label="Find a vehicle" />
        </label>
      </div>
      <div class="list lm-list">
        <div v-for="v in pager.rows.value" :key="v.id" class="list-row clickable" :class="{ sel: v.id === focusId }"
             role="button" tabindex="0" @click="select(v)" @keydown.enter="select(v)">
          <span class="dot" :class="freshness(v)"></span>
          <span class="grow">
            <div class="title">{{ v.local_name }}</div>
            <div class="sub">{{ v.registration_number }} · {{ v.latest?.has_gps_fix ? ago(v.latest.received_at) : 'No GPS fix' }}</div>
          </span>
          <span class="badge" :class="v.status">{{ v.status }}</span>
          <button v-if="canWrite" type="button" class="ghost icon-btn sm" title="Rename" aria-label="Rename vehicle" @click.stop="renaming = v"><Pencil :size="14" /></button>
        </div>
        <EmptyState v-if="!shown.length" compact :icon="SearchX" title="No match" />
      </div>
      <Pager :pager="pager" />
    </div>
  </div>

  <RenameVehicleModal v-if="renaming" :vehicle="renaming" @close="renaming = null" @saved="onRenamed" />
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { LocateFixed, Pencil, Search, SearchX, Maximize2, ChevronRight } from 'lucide-vue-next'
import { getVehicles, getVehicleTrack } from '../api'
import { recentTrack } from '../recent-track'
import { auth } from '../auth'
import { freshness, ago, fmt } from '../util'
import FleetMap from '../components/FleetMap.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import EmptyState from '../components/EmptyState.vue'
import RenameVehicleModal from '../components/RenameVehicleModal.vue'

const canWrite = computed(() => auth.user?.may_write !== false)
const vehicles = ref([])
const loading = ref(true)
const focusId = ref(null)
const renaming = ref(null)
const q = ref('')
let timer

const markers = computed(() => vehicles.value
  .filter((v) => v.latest?.has_gps_fix && v.latest.latitude != null)
  .map((v) => ({ id: v.id, lat: v.latest.latitude, lng: v.latest.longitude, label: v.local_name, status: v.status, speed: fmt(v.latest.speed_kmph, 0) })))
const focused = computed(() => vehicles.value.find((v) => v.id === focusId.value) || null)
const shown = computed(() => {
  const t = q.value.trim().toLowerCase()
  return t ? vehicles.value.filter((v) => [v.local_name, v.registration_number].some((x) => x?.toLowerCase().includes(t))) : vehicles.value
})

const pager = usePaging(shown, 10, [q])

function select(v) {
  focusId.value = focusId.value === v.id ? null : v.id
  if (focusId.value != null && matchMedia('(max-width: 1199px)').matches) window.scrollTo({ top: 0, behavior: 'smooth' })
}

function onRenamed(name) {
  const veh = vehicles.value.find((x) => x.id === renaming.value.id)
  if (veh) veh.local_name = name
  renaming.value = null
}

// the focused truck's recent road: drawn on the map and used by its Google Maps button
const focusTrack = ref([])
async function loadTrack() {
  const id = focusId.value
  if (id == null) { focusTrack.value = []; return }
  try {
    const pts = recentTrack(await getVehicleTrack(id, 300))
    if (focusId.value === id) focusTrack.value = pts
  } catch (e) { /* keep the pin-only view */ }
}
watch(focusId, () => { focusTrack.value = []; loadTrack() })

async function load() {
  loadTrack()
  try { vehicles.value = await getVehicles() }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.lm-layout { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 16px; align-items: start; }
.lm-map-card :deep(.lm-map) { height: calc(100vh - 186px); min-height: 400px; }
.lm-map-skel { height: calc(100vh - 186px); min-height: 400px; }
.lm-list { max-height: calc(100vh - 306px); min-height: 280px; overflow-y: auto; }
.list-row.sel { background: var(--brand-soft); box-shadow: inset 3px 0 0 var(--brand); }
.coord-row { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 24px; padding: 12px 18px; border-top: 1px solid var(--border); }
.coord-row > div { display: flex; flex-direction: column; gap: 1px; }
.coord-row .k { font-size: 11.5px; color: var(--muted); font-weight: 600; }
.coord-row b { color: var(--ink-strong); font-size: 13.5px; }
@media (max-width: 1199px) {
  .lm-layout { grid-template-columns: minmax(0, 1fr); }
  .lm-map-card :deep(.lm-map), .lm-map-skel { height: clamp(280px, 52dvh, 480px); min-height: 0; }
  .lm-list { max-height: none; min-height: 0; }
}
@media (max-width: 720px) { .coord-row { padding: 12px 14px; } .coord-row .btn { margin-left: 0 !important; width: 100%; } }
</style>
