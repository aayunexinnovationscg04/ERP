<template>
  <PageHeader title="Pilots" description="Drivers registered to your fleet and the vehicle each one is currently assigned to." />

  <div v-if="loading" class="kpis"><div class="skel sk-chip" v-for="n in 3" :key="n"></div></div>
  <div v-else class="kpis">
    <StatTile label="Pilots" :value="pilots.length" :icon="Users" tone="blue" />
    <StatTile label="On a vehicle" :value="assignedCount" :icon="UserCheck" tone="green" />
    <StatTile label="Vehicles without a pilot" :value="unassigned.length" :icon="UserX" :tone="unassigned.length ? 'amber' : 'gray'" />
  </div>

  <div class="card flush">
    <div class="card-head" v-if="loading || pilots.length">
      <label class="search">
        <Search :size="16" />
        <input v-model="q" type="search" placeholder="Search name, phone, vehicle…" aria-label="Search pilots" />
      </label>
    </div>
    <div v-if="loading" class="card-body"><div class="skel sk-row" v-for="n in 5" :key="n"></div></div>
    <EmptyState v-else-if="!pilots.length" :icon="IdCard" title="No pilots yet"
      text="Pilots added by your administrator will show up here with their assigned vehicle." />
    <EmptyState v-else-if="!shown.length" compact :icon="SearchX" title="No matching pilots" />
    <template v-else>
      <div class="table-wrap hide-sm">
        <table>
          <thead><tr><th>Pilot</th><th>Phone</th><th>Licence</th><th>Assigned vehicle</th><th style="width:48px"></th></tr></thead>
          <tbody>
            <tr v-for="p in shown" :key="p.id" class="clickable" @click="$router.push(`/pilots/${p.id}`)">
              <td><div class="cell-with-icon"><span class="p-avatar">{{ initials(p.name) }}</span><span class="cell-main">{{ p.name }}</span></div></td>
              <td class="nowrap">{{ p.phone || '—' }}</td>
              <td class="muted">{{ p.license_no || '—' }}</td>
              <td>
                <template v-if="p.assigned_vehicle"><div class="cell-main" style="font-weight:600">{{ p.assigned_vehicle.local_name }}</div><div class="cell-sub">{{ p.assigned_vehicle.registration_number }}</div></template>
                <span v-else class="badge offline">Unassigned</span>
              </td>
              <td><router-link :to="`/pilots/${p.id}`" class="row-link" title="Open pilot" @click.stop><ChevronRight :size="17" /></router-link></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="list show-sm">
        <router-link v-for="p in shown" :key="p.id" :to="`/pilots/${p.id}`" class="list-row">
          <span class="p-avatar">{{ initials(p.name) }}</span>
          <span class="grow">
            <div class="title">{{ p.name }}</div>
            <div class="sub">{{ p.assigned_vehicle ? p.assigned_vehicle.local_name + ' · ' + p.assigned_vehicle.registration_number : 'No vehicle assigned' }}</div>
          </span>
          <ChevronRight :size="17" class="muted" />
        </router-link>
      </div>
    </template>
  </div>

  <div v-if="!loading && unassigned.length" class="card flush section">
    <div class="card-head"><div class="card-head-title"><UserX :size="17" /><div><h2>Vehicles without a pilot</h2>
      <div class="card-sub">Pilot assignment is managed by your administrator</div></div></div></div>
    <div class="list">
      <router-link v-for="v in unassigned" :key="v.id" :to="`/vehicles/${v.id}`" class="list-row">
        <span class="icon-chip gray"><Truck :size="16" /></span>
        <span class="grow"><div class="title">{{ v.local_name }}</div><div class="sub">{{ v.registration_number }}</div></span>
        <span class="badge" :class="v.status">{{ v.status }}</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Users, UserCheck, UserX, IdCard, Search, SearchX, ChevronRight, Truck } from 'lucide-vue-next'
import { getPilots, getVehicles } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'

const pilots = ref([])
const vehicles = ref([])
const loading = ref(true)
const q = ref('')

const assignedCount = computed(() => pilots.value.filter((p) => p.assigned_vehicle).length)
const unassigned = computed(() => vehicles.value.filter((v) => !v.active_pilot))
const shown = computed(() => {
  const t = q.value.trim().toLowerCase()
  return pilots.value.filter((p) => !t || [p.name, p.phone, p.license_no, p.assigned_vehicle?.local_name, p.assigned_vehicle?.registration_number]
    .some((x) => x?.toLowerCase().includes(t)))
})
function initials(n) {
  const parts = (n || '?').trim().split(/\s+/)
  return ((parts[0]?.[0] || '') + (parts[1]?.[0] || '')).toUpperCase()
}

onMounted(async () => {
  try {
    const [p, v] = await Promise.all([getPilots(), getVehicles()])
    pilots.value = p
    vehicles.value = v
  } catch (e) { /* keep empty */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.p-avatar {
  width: 34px; height: 34px; border-radius: 50%; flex: none; display: grid; place-items: center;
  background: var(--info-soft); color: var(--info); font-size: 12.5px; font-weight: 800;
}
</style>
