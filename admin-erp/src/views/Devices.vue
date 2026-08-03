<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Device Management</span>
      <h1 class="ico"><Cpu :size="20" /> Devices</h1>
    </div>
  </div>
  <p class="hint">ESP32 fleet across every company. Illustrative preview — the device API does not yet return a per-device company tag, so rows below are simulated (company names are real).</p>

  <div class="chiprow" v-if="!loading">
    <div class="chip"><span class="chip-n num">{{ devices.length }}</span><span class="chip-l">Total devices</span></div>
    <div class="chip" style="border-top-color:var(--green)"><span class="chip-n num">{{ onlineCount }}</span><span class="chip-l">Online</span></div>
    <div class="chip flag"><span class="chip-n num">{{ devices.length - onlineCount }}</span><span class="chip-l">Offline</span></div>
    <div class="chip" style="border-top-color:var(--amber)"><span class="chip-n num">{{ faultCount }}</span><span class="chip-l">Sensor faults</span></div>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Device ID</th><th>Company</th><th>Health</th><th>Sensors</th><th>Status</th><th>Last seen</th></tr></thead>
      <tbody v-if="loading">
        <tr v-for="n in 8" :key="n"><td colspan="6" style="padding:6px 13px"><div class="skel sk-row" style="margin:0"></div></td></tr>
      </tbody>
      <tbody v-else>
        <motion.tr
          v-for="(d, idx) in devices" :key="d.id"
          :initial="{ opacity: 0, y: 6 }" :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: 0.14, delay: Math.min(idx, 12) * 0.015, ease: [0.4, 0, 0.2, 1] }"
        >
          <td>{{ d.device_id }}</td>
          <td class="muted">{{ d.company }}</td>
          <td><span class="badge" :class="healthClass(d.health)">{{ healthLabel(d.health) }}</span></td>
          <td><span class="badge" :class="d.sensorOk ? 'active' : 'warning'">{{ d.sensorOk ? 'OK' : 'Fault' }}</span></td>
          <td>
            <span class="ico">
              <span class="dot" :class="d.online ? 'green' : 'gray'"></span>
              {{ d.online ? 'Online' : 'Offline' }}
            </span>
          </td>
          <td class="muted">{{ d.lastSeen }}</td>
        </motion.tr>
      </tbody>
    </table>
    <div v-if="!loading" class="table-foot">{{ devices.length }} devices</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { motion } from 'motion-v'
import { Cpu } from 'lucide-vue-next'
import { getCompanies } from '../api'

const devices = ref([])
const loading = ref(true)

function seeded(seed) {
  const x = Math.sin(seed * 17.31 + 5.19) * 91827.53
  return x - Math.floor(x)
}
const healthLevels = ['healthy', 'warning', 'critical']
function healthLabel(h) { return h === 'healthy' ? 'Healthy' : h === 'warning' ? 'Attention' : 'Critical' }
function healthClass(h) { return h === 'healthy' ? 'active' : h === 'warning' ? 'warning' : 'critical' }

const onlineCount = computed(() => devices.value.filter((d) => d.online).length)
const faultCount = computed(() => devices.value.filter((d) => !d.sensorOk).length)

function relTime(minsAgo) {
  if (minsAgo < 1) return 'just now'
  if (minsAgo < 60) return `${minsAgo}m ago`
  const h = Math.floor(minsAgo / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

async function load() {
  try {
    const companies = await getCompanies()
    const names = companies.length ? companies.map((c) => c.name) : ['Demo Logistics Co.']
    const count = Math.max(10, names.length * 3)
    devices.value = Array.from({ length: count }, (_, i) => {
      const seed = i + 1
      const online = seeded(seed * 3 + 1) > 0.22
      const health = healthLevels[Math.floor(seeded(seed * 5 + 2) * (online ? 2 : 3))]
      const sensorOk = seeded(seed * 7 + 3) > 0.15
      const minsAgo = online ? Math.floor(seeded(seed * 11 + 4) * 12) : 15 + Math.floor(seeded(seed * 13 + 5) * 4000)
      return {
        id: seed,
        device_id: `esp32-${String(seed).padStart(3, '0')}`,
        company: names[i % names.length],
        online, health, sensorOk,
        lastSeen: relTime(minsAgo),
      }
    })
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>
