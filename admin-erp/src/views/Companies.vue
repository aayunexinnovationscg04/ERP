<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Company Management</span>
      <h1 class="ico"><Building2 :size="20" /> Companies</h1>
    </div>
  </div>
  <p class="hint">Every tenant registered on the platform. Fleet size and growth are illustrative pending a dedicated per-company aggregation endpoint.</p>

  <div class="chiprow" v-if="!loading">
    <div class="chip"><span class="chip-n num">{{ companies.length }}</span><span class="chip-l">Total companies</span></div>
    <div class="chip" style="border-top-color:var(--green)"><span class="chip-n num">{{ activeCount }}</span><span class="chip-l">Active</span></div>
    <div class="chip" style="border-top-color:var(--slate)"><span class="chip-n num">{{ companies.length - activeCount }}</span><span class="chip-l">Inactive</span></div>
    <div class="chip" style="border-top-color:var(--role-manager)"><span class="chip-n num">{{ totalFleet }}</span><span class="chip-l">Fleet across platform</span></div>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Company</th><th>Status</th><th>Active fleet</th><th>30-day trend</th><th>Registered</th></tr></thead>
      <tbody v-if="loading">
        <tr v-for="n in 6" :key="n"><td colspan="5" style="padding:6px 13px"><div class="skel sk-row" style="margin:0"></div></td></tr>
      </tbody>
      <tbody v-else-if="!companies.length">
        <tr><td colspan="5" class="muted" style="text-align:center;padding:22px">No companies registered yet.</td></tr>
      </tbody>
      <tbody v-else>
        <motion.tr
          v-for="(c, idx) in enriched" :key="c.id"
          :initial="{ opacity: 0, y: 6 }" :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: 0.16, delay: Math.min(idx, 10) * 0.02, ease: [0.4, 0, 0.2, 1] }"
        >
          <td>{{ c.name }}<div class="muted" style="font-size:12px">{{ c.slug }}</div></td>
          <td><span class="badge" :class="c.status === 'active' ? 'active' : 'offline'">{{ c.status === 'active' ? 'Active' : 'Inactive' }}</span></td>
          <td class="num">{{ c.fleet }} vehicles</td>
          <td>
            <span class="ico" :style="{ color: c.trend >= 0 ? 'var(--green)' : 'var(--red)' }">
              <component :is="c.trend >= 0 ? TrendingUp : TrendingDown" :size="14" />
              {{ c.trend >= 0 ? '+' : '' }}{{ c.trend }}%
            </span>
          </td>
          <td class="muted">{{ fmtDate(c.created_at) }}</td>
        </motion.tr>
      </tbody>
    </table>
    <div v-if="!loading" class="table-foot">{{ companies.length }} {{ companies.length === 1 ? 'company' : 'companies' }} · source: /admin/companies/</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { motion } from 'motion-v'
import { Building2, TrendingUp, TrendingDown } from 'lucide-vue-next'
import { getCompanies } from '../api'

const companies = ref([])
const loading = ref(true)

const activeCount = computed(() => companies.value.filter((c) => c.status === 'active').length)

// deterministic pseudo-random (seeded by company id) so illustrative fleet
// size / trend numbers stay stable across reloads instead of flickering
function seeded(seed) {
  const x = Math.sin(seed * 9301 + 49297) * 233280
  return x - Math.floor(x)
}
function fleetFor(id) { return 3 + Math.floor(seeded(id * 7 + 1) * 45) }
function trendFor(id) { return Math.round((seeded(id * 13 + 3) * 30 - 10) * 10) / 10 }

const enriched = computed(() => companies.value.map((c) => ({
  ...c, fleet: fleetFor(c.id), trend: trendFor(c.id),
})))
const totalFleet = computed(() => enriched.value.reduce((s, c) => s + c.fleet, 0))

function fmtDate(s) { return s ? new Date(s).toLocaleDateString() : '—' }

async function load() {
  try { companies.value = await getCompanies() } finally { loading.value = false }
}
onMounted(load)
</script>
