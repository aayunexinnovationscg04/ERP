<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Company Management</span>
      <h1 class="ico"><BarChart :size="20" /> Company Analytics</h1>
    </div>
  </div>
  <p class="hint">Per-company usage and growth, presentational until a dedicated analytics aggregation service lands.</p>

  <div v-if="loading" class="grid-2">
    <div class="card" style="padding:16px"><div class="skel skel-line md"></div><div class="skel sk-row" v-for="n in 5" :key="n"></div></div>
    <div class="card" style="padding:16px"><div class="skel skel-line md"></div><div class="skel sk-row" v-for="n in 5" :key="n"></div></div>
  </div>

  <div v-else class="grid-2">
    <div class="card" style="padding:16px">
      <p class="section-title" style="margin-bottom:14px">Active users by company (30d)</p>
      <div v-if="rows.length" class="barchart">
        <div class="brow" v-for="d in rows" :key="d.id">
          <span class="blabel" :title="d.name">{{ d.name }}</span>
          <svg class="btrack" width="100%" height="12" role="img" :aria-label="`${d.name}: ${d.activeUsers} active users`">
            <rect width="100%" height="12" rx="3" fill="var(--surface-3)" />
            <rect :width="pct(d.activeUsers) + '%'" height="12" rx="3" fill="var(--brand)" />
          </svg>
          <span class="bval">{{ d.activeUsers }}</span>
        </div>
      </div>
      <div v-else class="empty">No companies yet</div>
    </div>

    <div class="card" style="padding:16px">
      <p class="section-title" style="margin-bottom:14px">Fleet growth (month over month)</p>
      <div v-if="rows.length" class="barchart">
        <div class="brow" v-for="d in rows" :key="d.id">
          <span class="blabel" :title="d.name">{{ d.name }}</span>
          <svg class="btrack" width="100%" height="12" role="img" :aria-label="`${d.name}: ${d.growth}% growth`">
            <rect width="100%" height="12" rx="3" fill="var(--surface-3)" />
            <rect :width="growthPct(d.growth) + '%'" height="12" rx="3" :fill="d.growth >= 0 ? 'var(--green)' : 'var(--red)'" />
          </svg>
          <span class="bval" :style="{ color: d.growth >= 0 ? 'var(--green)' : 'var(--red)' }">{{ d.growth >= 0 ? '+' : '' }}{{ d.growth }}%</span>
        </div>
      </div>
      <div v-else class="empty">No companies yet</div>
    </div>
  </div>

  <div class="card" style="padding:6px 0;margin-top:18px" v-if="!loading">
    <table>
      <thead><tr><th>Company</th><th>Active users</th><th>Sessions (30d)</th><th>Avg. session</th><th>Fleet growth</th></tr></thead>
      <tbody v-if="!rows.length"><tr><td colspan="5" class="muted" style="text-align:center;padding:22px">No companies registered yet.</td></tr></tbody>
      <tbody v-else>
        <tr v-for="d in rows" :key="d.id">
          <td>{{ d.name }}</td>
          <td class="num">{{ d.activeUsers }}</td>
          <td class="num">{{ d.sessions.toLocaleString() }}</td>
          <td class="num">{{ d.avgSessionMin }} min</td>
          <td class="num" :style="{ color: d.growth >= 0 ? 'var(--green)' : 'var(--red)' }">{{ d.growth >= 0 ? '+' : '' }}{{ d.growth }}%</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { BarChart } from 'lucide-vue-next'
import { getCompanies } from '../api'

const companies = ref([])
const loading = ref(true)

function seeded(seed) {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453
  return x - Math.floor(x)
}

const rows = computed(() => companies.value.map((c) => {
  const activeUsers = 4 + Math.floor(seeded(c.id * 3 + 1) * 60)
  const sessions = activeUsers * (8 + Math.floor(seeded(c.id * 5 + 2) * 20))
  const avgSessionMin = 6 + Math.floor(seeded(c.id * 7 + 3) * 24)
  const growth = Math.round((seeded(c.id * 11 + 4) * 40 - 14) * 10) / 10
  return { id: c.id, name: c.name, activeUsers, sessions, avgSessionMin, growth }
}))
const maxActive = computed(() => Math.max(1, ...rows.value.map((d) => d.activeUsers)))
const maxGrowthAbs = computed(() => Math.max(1, ...rows.value.map((d) => Math.abs(d.growth))))
function pct(n) { return Math.max(4, (n / maxActive.value) * 100) }
function growthPct(n) { return Math.max(4, (Math.abs(n) / maxGrowthAbs.value) * 100) }

async function load() {
  try { companies.value = await getCompanies() } finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.barchart { display: flex; flex-direction: column; gap: 13px; }
.brow { display: grid; grid-template-columns: 100px 1fr 40px; align-items: center; gap: 12px; }
.blabel { font-size: 12px; font-weight: 700; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bval { font-size: 13px; font-weight: 800; text-align: right; font-variant-numeric: tabular-nums; }
.btrack { display: block; }
.empty { color: var(--muted); font-size: 13px; text-align: center; padding: 16px 0; }
</style>
