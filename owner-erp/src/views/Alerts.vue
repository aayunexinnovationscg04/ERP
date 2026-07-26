<template>
  <div class="topbar">
    <h1>Alerts</h1>
    <div class="row">
      <button :class="{ primary: filter === 'open' }" @click="setFilter('open')">Open</button>
      <button :class="{ primary: filter === '' }" @click="setFilter('')">All</button>
    </div>
  </div>

  <div v-if="loading" style="padding:2px 0">
    <div class="skel sk-row" v-for="n in 5" :key="n"></div>
  </div>

  <div v-else class="card" style="padding:6px 0">
    <table>
      <thead>
        <tr><th>Severity</th><th>Type</th><th>Title</th><th>Vehicle</th><th>When</th><th></th></tr>
      </thead>
      <tbody>
        <tr v-for="a in alerts" :key="a.id">
          <td><span class="badge" :class="a.severity">{{ a.severity }}</span></td>
          <td class="muted">{{ a.type }}</td>
          <td>{{ a.title }}<div class="muted" style="font-size:12px">{{ a.message }}</div></td>
          <td>{{ a.vehicle_reg || a.device_id || '—' }}</td>
          <td class="muted">{{ ago(a.created_at) }}</td>
          <td>
            <button v-if="a.status === 'open'" @click="ack(a)">Acknowledge</button>
            <span v-else class="muted">{{ a.status }}</span>
          </td>
        </tr>
        <tr v-if="!alerts.length"><td colspan="6" class="muted" style="padding:16px">No alerts.</td></tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { getAlerts, ackAlert } from '../api'
import { ago } from '../util'
import { toast } from '../toast'

const alerts = ref([])
const filter = ref('open')
const loading = ref(true)

async function load() {
  loading.value = true
  try { alerts.value = await getAlerts(filter.value ? { status: filter.value } : {}) }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
function setFilter(f) { filter.value = f; load() }
async function ack(a) {
  try {
    await ackAlert(a.id)
    toast.success('Alert acknowledged')
    load()
  } catch (e) { toast.error('Could not acknowledge alert') }
}

onMounted(load)
</script>
