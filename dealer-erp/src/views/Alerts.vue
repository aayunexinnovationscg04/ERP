<template>
  <div class="topbar">
    <h1>Alerts</h1>
    <div class="row seg">
      <button :class="{ primary: filter === 'open' }" @click="setFilter('open')">Open</button>
      <button :class="{ primary: filter === '' }" @click="setFilter('')">All</button>
    </div>
  </div>

  <p v-if="!canWrite" class="viewonly" style="margin:-8px 0 14px"><Lock :size="14" /> View-only — ask an admin to enable editing.</p>

  <div v-if="loading" class="kpis">
    <div class="skel sk-chip" v-for="n in 3" :key="n"></div>
  </div>
  <div v-else class="kpis">
    <motion.div class="card kpi glow-crit" :while-hover="{ y: -2 }">
      <TriangleAlert :size="16" class="ic" /><div class="n">{{ criticalCount }}</div><div class="l">Critical</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <TriangleAlert :size="16" class="ic" /><div class="n">{{ warningCount }}</div><div class="l">Warning</div>
    </motion.div>
    <motion.div class="card kpi glow-blue" :while-hover="{ y: -2 }">
      <Info :size="16" class="ic" /><div class="n">{{ infoCount }}</div><div class="l">Info</div>
    </motion.div>
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
        <motion.tr v-for="(a, i) in alerts" :key="a.id" :class="a.severity"
          :initial="{ opacity: 0, y: 6 }" :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: .2, delay: Math.min(i, 12) * .025, ease: [.4, 0, .2, 1] }">
          <td>
            <span class="icon-chip sm" :class="chipClass[a.severity]"><TriangleAlert v-if="a.severity !== 'info'" :size="14" /><Info v-else :size="14" /></span>
            <span class="badge" :class="a.severity">{{ a.severity }}</span>
          </td>
          <td class="muted">{{ a.type_label || a.type }}</td>
          <td>{{ a.title }}<div class="muted" style="font-size:12px">{{ a.message }}</div></td>
          <td>{{ a.vehicle_reg || a.device_id || '—' }}</td>
          <td class="muted">{{ ago(a.created_at) }}</td>
          <td>
            <button v-if="a.status === 'open' && canWrite" @click="ack(a)">Acknowledge</button>
            <span v-else class="muted">{{ a.status }}</span>
          </td>
        </motion.tr>
        <tr v-if="!alerts.length"><td colspan="6" class="muted" style="padding:16px">No alerts.</td></tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { Lock, TriangleAlert, Info } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { getAlerts, ackAlert } from '../api'
import { auth } from '../auth'
import { ago } from '../util'
import { toast } from '../toast'

const canWrite = computed(() => auth.user?.may_write !== false)
const alerts = ref([])
const filter = ref('open')
const loading = ref(true)
const chipClass = { critical: 'crit', warning: 'amber', info: 'blue' }

const criticalCount = computed(() => alerts.value.filter((a) => a.severity === 'critical').length)
const warningCount = computed(() => alerts.value.filter((a) => a.severity === 'warning').length)
const infoCount = computed(() => alerts.value.filter((a) => a.severity === 'info').length)

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

<style scoped>
.seg { background: var(--surface-2); border: 1px solid var(--border); padding: 3px; border-radius: var(--radius-pill); gap: 2px; }
.seg button { border: none; background: none; padding: 7px 16px; border-radius: var(--radius-pill); }
.seg button.primary { box-shadow: none; }
.seg button:not(.primary):hover { background: var(--surface-3); }
</style>
