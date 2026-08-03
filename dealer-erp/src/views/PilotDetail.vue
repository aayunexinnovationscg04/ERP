<template>
  <div class="topbar">
    <div class="row" style="gap:12px">
      <button type="button" class="back-btn" @click="$router.back()" title="Back">
        <ArrowLeft :size="17" />
      </button>
      <h1><router-link to="/pilots" class="muted">Pilots</router-link> / {{ d?.name || '…' }}</h1>
    </div>
  </div>

  <div v-if="loading" class="card" style="padding:16px">
    <div class="skel skel-line lg"></div>
    <div class="skel skel-line md"></div>
    <div class="skel skel-line sm"></div>
  </div>

  <template v-else>
    <p class="section-title">Assigned Driver</p>
    <div class="card" style="padding:16px 18px">
      <div class="kvs">
        <div><span class="muted">Name</span><b>{{ d.name }}</b></div>
        <div><span class="muted">Phone</span><b>{{ d.phone || '—' }}</b></div>
        <div><span class="muted">License</span><b>{{ d.license_no || '—' }}</b></div>
        <div>
          <span class="muted">Assigned vehicle</span>
          <b v-if="d.assigned_vehicle">
            <router-link :to="`/vehicles/${d.assigned_vehicle.id}`">
              {{ d.assigned_vehicle.local_name }} · {{ d.assigned_vehicle.registration_number }}
            </router-link>
          </b>
          <b v-else class="muted">Not assigned</b>
        </div>
      </div>
    </div>

    <p class="section-title">Driver Attendance</p>
    <div class="card" style="padding:6px 0">
      <table>
        <thead><tr><th>Date</th><th>Status</th><th>Notes</th></tr></thead>
        <tbody>
          <tr v-for="a in d.attendance" :key="a.id">
            <td>{{ a.date }}</td>
            <td><span class="badge" :class="attendanceBadge[a.status]">{{ a.status_label }}</span></td>
            <td class="muted">{{ a.notes || '—' }}</td>
          </tr>
          <tr v-if="!d.attendance?.length"><td colspan="3" class="muted" style="padding:14px">No attendance recorded yet.</td></tr>
        </tbody>
      </table>
    </div>

    <p class="section-title">Overspeed Violations</p>
    <div class="card" style="padding:6px 0">
      <table>
        <thead><tr><th>When</th><th>Speed</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="a in overspeed" :key="a.id">
            <td>{{ new Date(a.created_at).toLocaleString() }}</td>
            <td>{{ a.meta?.speed_kmph }} km/h <span class="muted">(limit {{ a.meta?.limit }})</span></td>
            <td><span class="badge" :class="a.status === 'open' ? 'critical' : 'offline'">{{ a.status }}</span></td>
          </tr>
          <tr v-if="!overspeed.length"><td colspan="3" class="muted" style="padding:14px">
            {{ d.assigned_vehicle ? 'No overspeed violations on their current vehicle.' : 'No vehicle assigned — nothing to check.' }}
          </td></tr>
        </tbody>
      </table>
    </div>

    <p class="section-title">Driver Salary Information</p>
    <div class="card" style="padding:16px 18px">
      <div class="fh-value" v-if="d.monthly_salary">₹{{ fmt(d.monthly_salary, 0) }} <span class="fh-unit">/ month</span></div>
      <p v-else class="muted" style="margin:0">Not set — ask an admin to add it in Django Admin.</p>
    </div>
  </template>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import { getDriver, getAlerts } from '../api'
import { fmt } from '../util'

const props = defineProps({ id: [String, Number] })
const d = ref(null)
const overspeed = ref([])
const loading = ref(true)
const attendanceBadge = { present: 'active', absent: 'critical', half_day: 'idle', leave: 'offline' }

async function load() {
  try {
    d.value = await getDriver(props.id)
    if (d.value.assigned_vehicle) {
      overspeed.value = await getAlerts({ vehicle: d.value.assigned_vehicle.id, type: 'overspeed' })
    }
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.back-btn {
  flex: none; width: 34px; height: 34px; padding: 0; display: grid; place-items: center;
  border-radius: var(--radius-sm); color: var(--text);
}
.back-btn:hover { background: var(--surface-2); }

.kvs { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 18px; }
.kvs div { display: flex; flex-direction: column; gap: 2px; }
.kvs b { font-size: 15px; }

.fh-value { font-size: 26px; font-weight: 800; letter-spacing: -.01em; }
.fh-unit { font-size: 14px; font-weight: 600; color: var(--muted); }

.card + .section-title { margin-top: 28px; }
</style>
