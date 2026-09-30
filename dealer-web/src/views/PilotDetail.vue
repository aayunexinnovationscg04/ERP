<template>
  <PageHeader :title="d ? d.name : 'Pilot'" :back="{ to: '/pilots', label: 'Pilots' }">
    <template #description>
      <span v-if="d">{{ d.assigned_vehicle ? d.assigned_vehicle.local_name + ' · ' + d.assigned_vehicle.registration_number : 'No vehicle assigned' }}<template v-if="d.phone"> · {{ d.phone }}</template></span>
    </template>
    <a v-if="d?.phone" :href="`tel:${d.phone}`" class="btn"><Phone :size="16" /> Call</a>
  </PageHeader>

  <div v-if="loading">
    <div class="kpis"><div class="skel sk-chip" v-for="n in 4" :key="n"></div></div>
    <div class="skel sk-hero"></div>
  </div>

  <EmptyState v-else-if="!d" class="card" :icon="IdCard" title="Pilot not found">
    <router-link to="/pilots" class="btn">Back to pilots</router-link>
  </EmptyState>

  <template v-else>
    <div class="kpis">
      <StatTile label="Attendance" :value="attPct == null ? '—' : attPct" :unit="attPct == null ? '' : '%'" :icon="CalendarCheck" tone="green" />
      <StatTile label="Absences" :value="attCounts.absent" :icon="CalendarX" :tone="attCounts.absent ? 'crit' : 'gray'" />
      <StatTile label="Overspeed" :value="overspeed.length" :icon="Gauge" :tone="overspeed.length ? 'amber' : 'gray'" />
      <StatTile label="Monthly salary" :value="d.monthly_salary ? '₹' + Number(d.monthly_salary).toLocaleString('en-IN') : '—'" :icon="Wallet" tone="navy" />
    </div>

    <div class="grid-2">
      <div class="card flush">
        <div class="card-head"><div class="card-head-title"><CalendarCheck :size="17" /><h2>Attendance</h2></div></div>
        <div v-if="d.attendance?.length" class="table-wrap">
          <table>
            <thead><tr><th>Date</th><th>Status</th><th class="hide-sm">Notes</th></tr></thead>
            <tbody>
              <tr v-for="a in attPager.rows.value" :key="a.id">
                <td class="nowrap">{{ fmtDate(a.date) }}</td>
                <td><span class="badge" :class="attendanceBadge[a.status]">{{ a.status_label }}</span></td>
                <td class="hide-sm muted">{{ a.notes || '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <Pager v-if="d.attendance?.length" :pager="attPager" />
        <EmptyState v-else compact :icon="CalendarCheck" title="No attendance recorded yet" />
      </div>

      <div class="stack">
        <div class="card">
          <div class="card-head"><div class="card-head-title"><IdCard :size="17" /><h2>Profile</h2></div></div>
          <div class="card-body">
            <div class="kvs">
              <div><span class="k">Name</span><span class="v">{{ d.name }}</span></div>
              <div><span class="k">Phone</span><span class="v">{{ d.phone || '—' }}</span></div>
              <div><span class="k">Licence</span><span class="v">{{ d.license_no || '—' }}</span></div>
              <div><span class="k">Vehicle</span>
                <span class="v" v-if="d.assigned_vehicle"><router-link :to="`/vehicles/${d.assigned_vehicle.id}`">{{ d.assigned_vehicle.local_name }}</router-link></span>
                <span class="v muted" v-else>Not assigned</span></div>
            </div>
          </div>
        </div>

        <div class="card flush">
          <div class="card-head"><div class="card-head-title"><Gauge :size="17" /><h2>Overspeed violations</h2></div></div>
          <div v-if="overspeed.length" class="list">
            <div v-for="a in osPager.rows.value" :key="a.id" class="list-row">
              <span class="grow">
                <div class="title" v-if="a.meta?.speed_kmph != null">{{ a.meta.speed_kmph }} km/h <span class="muted" style="font-weight:500" v-if="a.meta.limit != null">· limit {{ a.meta.limit }}</span></div>
                <div class="title" v-else>{{ a.title }}</div>
                <div class="sub">{{ new Date(a.created_at).toLocaleString('en-IN', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) }}</div>
              </span>
              <span class="badge" :class="a.status === 'open' ? 'critical' : 'offline'">{{ a.status }}</span>
            </div>
          </div>
          <Pager v-if="overspeed.length" :pager="osPager" />
          <EmptyState v-else compact :icon="ShieldCheck"
            :title="d.assigned_vehicle ? 'No overspeed violations' : 'No vehicle assigned'"
            />
        </div>
      </div>
    </div>
  </template>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Phone, IdCard, CalendarCheck, CalendarX, Gauge, Wallet, ShieldCheck } from 'lucide-vue-next'
import { getPilot, getAlerts } from '../api'
import PageHeader from '../components/PageHeader.vue'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const props = defineProps({ id: [String, Number] })
const d = ref(null)
const overspeed = ref([])
const loading = ref(true)
const attendanceBadge = { present: 'active', absent: 'critical', half_day: 'idle', leave: 'offline' }

const attCounts = computed(() => {
  const c = { present: 0, absent: 0 }
  ;(d.value?.attendance || []).forEach((a) => { if (a.status in c) c[a.status]++ })
  return c
})
const attPct = computed(() => {
  const n = d.value?.attendance?.length
  return n ? Math.round((attCounts.value.present / n) * 100) : null
})
const attPager = usePaging(computed(() => d.value?.attendance || []), 10)
const osPager = usePaging(overspeed, 10)
function fmtDate(s) { return new Date(s + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'short', day: '2-digit', month: 'short' }) }

async function load() {
  try {
    d.value = await getPilot(props.id)
    if (d.value.assigned_vehicle) {
      overspeed.value = await getAlerts({ vehicle: d.value.assigned_vehicle.id, type: 'overspeed' })
    }
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(load)
</script>
