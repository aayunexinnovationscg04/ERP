<template>
  <div class="topbar">
    <h1>Alerts</h1>
    <div class="row">
      <button :class="{ primary: filter === 'open' }" @click="setFilter('open')">Open</button>
      <button :class="{ primary: filter === '' }" @click="setFilter('')">All</button>
    </div>
  </div>

  <div class="card" style="padding:6px 0">
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

const alerts = ref([])
const filter = ref('open')

async function load() {
  alerts.value = await getAlerts(filter.value ? { status: filter.value } : {})
}
function setFilter(f) { filter.value = f; load() }
async function ack(a) { await ackAlert(a.id); load() }

onMounted(load)
</script>
