<template>
  <div v-if="loading" class="grid-2">
    <div class="skel sk-map"></div>
    <div class="card card-body"><div class="skel sk-row" v-for="n in 5" :key="n"></div></div>
  </div>

  <div v-else-if="!vehicles.length" class="card">
    <EmptyState :icon="History" title="No route history yet" />
  </div>

  <template v-else>
    <div class="rh-bar">
      <label class="rh-pick">
        <span class="sr-only">Vehicle</span>
        <select v-model="vehicleId" aria-label="Vehicle">
          <option v-for="v in vehicles" :key="v.id" :value="v.id">{{ v.local_name }} · {{ v.registration_number }}</option>
        </select>
      </label>
    </div>
    <div class="kpis">
      <StatTile label="Trips recorded" :value="trips.length" :icon="RouteIcon" tone="blue" />
      <StatTile label="Distance" :value="fmt(totalKm, 0)" unit="km" :icon="Milestone" tone="navy" />
      <StatTile label="Fuel used" :value="fmt(totalFuel)" unit="L" :icon="Fuel" tone="brand" />
      <StatTile label="Top speed" :value="fmt(topSpeed, 0)" unit="km/h" :icon="Gauge" :tone="topSpeed > 80 ? 'amber' : 'green'" />
    </div>

    <div class="grid-2">
      <div class="card flush">
        <div class="card-head">
          <div class="card-head-title"><MapIcon :size="17" /><div><h2>{{ selTrip ? 'Trip on ' + dt(selTrip.started_at) : 'Recent track' }}</h2>
            <div v-if="selTrip && selTrip.start_lat == null" class="card-sub">No start/end position</div></div></div>
          <button v-if="selTrip" type="button" class="sm" @click="selTripId = null"><MapIcon :size="14" /> Recent track</button>
        </div>
        <div v-if="tripLoading" class="skel" style="height:440px;border-radius:0"></div>
        <FleetMap v-else :markers="markers" :track="mapTrack" :end-label="selTrip ? 'End' : 'Latest'" />
      </div>

      <div class="card flush">
        <div class="card-head"><div class="card-head-title"><History :size="17" /><h2>Trips</h2></div></div>
        <EmptyState v-if="!trips.length && !tripLoading" compact :icon="RouteIcon" title="No trips for this vehicle" />
        <div v-else class="list rh-list">
          <div v-for="t in pager.rows.value" :key="t.id" class="list-row clickable" :class="{ sel: t.id === selTripId }" role="button" tabindex="0"
               @click="selTripId = t.id" @keydown.enter="selTripId = t.id">
            <span class="icon-chip" :class="t.status === 'active' ? 'green' : 'gray'"><RouteIcon :size="16" /></span>
            <span class="grow">
              <div class="title">{{ dt(t.started_at) }}</div>
              <div class="sub">{{ fmt(t.distance_km) }} km · {{ duration(t) }} · max {{ fmt(t.max_speed_kmph, 0) }} km/h</div>
            </span>
            <span class="badge" :class="t.status === 'active' ? 'active' : 'offline'">{{ t.status === 'active' ? 'Live' : 'Done' }}</span>
          </div>
        </div>
        <Pager v-if="trips.length" :pager="pager" />
      </div>
    </div>
  </template>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { History, Route as RouteIcon, Map as MapIcon, Milestone, Fuel, Gauge } from 'lucide-vue-next'
import { getVehicles, getVehicleTrack, getVehicleTrips } from '../api'
import { fmt } from '../util'
import FleetMap from '../components/FleetMap.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'

const vehicles = ref([])
const vehicleId = ref(null)
const trips = ref([])
const track = ref([])
const loading = ref(true)
const tripLoading = ref(false)
const selTripId = ref(null)

const dt = (iso) => new Date(iso).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
function duration(t) {
  const end = t.ended_at ? new Date(t.ended_at) : new Date()
  const mins = Math.max(0, Math.round((end - new Date(t.started_at)) / 60000))
  return mins >= 60 ? `${Math.floor(mins / 60)}h ${mins % 60}m` : `${mins}m`
}

const vehicle = computed(() => vehicles.value.find((v) => v.id === vehicleId.value))
const selTrip = computed(() => trips.value.find((t) => t.id === selTripId.value) || null)
const totalKm = computed(() => trips.value.reduce((s, t) => s + (t.distance_km || 0), 0))
const totalFuel = computed(() => trips.value.reduce((s, t) => s + (t.fuel_consumed_litres || 0), 0))
const topSpeed = computed(() => trips.value.reduce((m, t) => Math.max(m, t.max_speed_kmph || 0), 0))

const pager = usePaging(trips, 10, [vehicleId])

const mapTrack = computed(() => {
  const t = selTrip.value
  if (t) return t.start_lat != null && t.end_lat != null ? [[t.start_lat, t.start_lng], [t.end_lat, t.end_lng]] : []
  return track.value.map((p) => [p.latitude, p.longitude])
})
const markers = computed(() => {
  const l = vehicle.value?.latest
  if (selTrip.value || !l?.has_gps_fix) return []
  return [{ id: vehicle.value.id, lat: l.latitude, lng: l.longitude, label: vehicle.value.local_name, status: vehicle.value.status }]
})

async function loadVehicle(id) {
  if (id == null) return
  tripLoading.value = true
  selTripId.value = null
  try {
    ;[trips.value, track.value] = await Promise.all([getVehicleTrips(id), getVehicleTrack(id, 1000)])
  } catch (e) { trips.value = []; track.value = [] }
  finally { tripLoading.value = false }
}
watch(vehicleId, loadVehicle)

onMounted(async () => {
  try {
    vehicles.value = await getVehicles()
    if (vehicles.value.length) vehicleId.value = vehicles.value[0].id
  } catch (e) { /* empty state */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.rh-bar { display: flex; margin-bottom: 12px; }
.rh-pick { width: 340px; max-width: 100%; }
.rh-list { max-height: 440px; overflow-y: auto; }
.list-row.sel { background: var(--brand-soft); box-shadow: inset 3px 0 0 var(--brand); }
@media (max-width: 720px) { .rh-pick { width: 100%; } .rh-list { max-height: none; } }
</style>
