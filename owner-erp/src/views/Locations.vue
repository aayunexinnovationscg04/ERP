<template>
  <div class="topbar">
    <h1>Locations</h1>
    <span class="muted">{{ vehicles.length }} vehicle(s)</span>
  </div>

  <div v-if="loading" style="padding:2px 0">
    <div class="skel sk-row" v-for="n in 4" :key="n"></div>
  </div>

  <div v-else class="loc-list">
    <div class="card loc-card" v-for="v in vehicles" :key="v.id">
      <div class="loc-row">
        <div class="loc-name">
          <span class="dot" :class="freshness(v)"></span>
          <button type="button" class="local-name-btn" @click="renaming = v" title="Rename">
            {{ v.local_name }} <Pencil :size="12" class="pencil" />
          </button>
          <span class="muted loc-reg">{{ v.registration_number }}</span>
        </div>
        <button type="button" class="see-loc-btn" @click="toggle(v)">
          <component :is="shownId === v.id ? ChevronUp : MapPin" :size="15" />
          {{ shownId === v.id ? 'Hide' : 'See current location' }}
        </button>
      </div>

      <div v-if="shownId === v.id" class="loc-detail">
        <template v-if="v.latest?.has_gps_fix">
          <FleetMap :markers="[{ id: v.id, lat: v.latest.latitude, lng: v.latest.longitude, label: v.local_name }]" />
          <div class="coord-row">
            <div><span class="muted">Latitude</span><b>{{ v.latest.latitude.toFixed(6) }}</b></div>
            <div><span class="muted">Longitude</span><b>{{ v.latest.longitude.toFixed(6) }}</b></div>
            <div><span class="muted">Updated</span><b>{{ ago(v.latest.received_at) }}</b></div>
          </div>
        </template>
        <p v-else class="muted" style="margin:0">No GPS fix on file yet for this truck.</p>
      </div>
    </div>

    <p v-if="!vehicles.length" class="muted">No vehicles yet.</p>
  </div>

  <RenameVehicleModal v-if="renaming" :vehicle="renaming" @close="renaming = null"
                       @saved="onRenamed" />
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { MapPin, ChevronUp, Pencil } from 'lucide-vue-next'
import { getVehicles } from '../api'
import { freshness, ago } from '../util'
import FleetMap from '../components/FleetMap.vue'
import RenameVehicleModal from '../components/RenameVehicleModal.vue'

const vehicles = ref([])
const loading = ref(true)
const shownId = ref(null)
const renaming = ref(null)
let timer

function toggle(v) { shownId.value = shownId.value === v.id ? null : v.id }

function onRenamed(name) {
  // Look up by id (not the captured `renaming` reference) in case the 15s
  // poll swapped `vehicles` for a fresh array while the modal was open —
  // mutating a stale object would silently not show up until the next poll.
  const veh = vehicles.value.find((x) => x.id === renaming.value.id)
  if (veh) veh.local_name = name
  renaming.value = null
}

async function load() {
  try { vehicles.value = await getVehicles() }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
.loc-list { display: grid; gap: 12px; }
.loc-card { padding: 14px 16px; }
.loc-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.loc-name { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; min-width: 0; }
.loc-reg { font-size: 12.5px; }

.local-name-btn {
  border: none; background: none; padding: 2px 0; font: inherit; font-size: 15px; font-weight: 700; color: var(--text);
  display: inline-flex; align-items: center; gap: 6px;
}
.local-name-btn .pencil { color: var(--muted); opacity: 0; transition: opacity var(--dur) var(--ease); }
.local-name-btn:hover .pencil { opacity: 1; }
.local-name-btn:hover { color: var(--brand); }

.see-loc-btn {
  display: inline-flex; align-items: center; gap: 7px; font-size: 13.5px; font-weight: 700;
  color: var(--brand); background: var(--brand-soft); border: 1px solid transparent;
  padding: 8px 14px; border-radius: var(--radius-pill); flex: none;
}
.see-loc-btn:hover { background: var(--brand-ring); }

.loc-detail { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--border); }
.coord-row {
  display: flex; flex-wrap: wrap; gap: 10px 24px; margin-top: 12px; font-size: 13.5px;
}
.coord-row > div { display: flex; flex-direction: column; gap: 2px; }
.coord-row b { font-variant-numeric: tabular-nums; }

@media (max-width: 600px) {
  .see-loc-btn { width: 100%; justify-content: center; }
  .loc-row { flex-direction: column; align-items: stretch; }
}
</style>
