<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Security &amp; Analytics</span>
      <h1 class="ico"><Flame :size="20" /> Fraud &amp; Fuel Theft Analytics</h1>
    </div>
  </div>
  <p class="hint">Flagged incidents across the platform. Illustrative sample — not wired to the derivation engine's alert store yet.</p>

  <div class="chiprow">
    <div class="chip flag"><span class="chip-n num">{{ openCount }}</span><span class="chip-l">Open incidents</span></div>
    <div class="chip" style="border-top-color:var(--green)"><span class="chip-n num">{{ resolvedCount }}</span><span class="chip-l">Resolved (30d)</span></div>
    <div class="chip"><span class="chip-n num">{{ incidents.length }}</span><span class="chip-l">Total (30d)</span></div>
  </div>

  <div class="grid-2">
    <div class="card" style="padding:6px 0">
      <table>
        <thead><tr><th>Company</th><th>Type</th><th>Severity</th><th>Detected</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="inc in incidents" :key="inc.id">
            <td>{{ inc.company }}<div class="muted" style="font-size:12px">{{ inc.vehicle }}</div></td>
            <td>{{ inc.type }}</td>
            <td><span class="badge" :class="sevClass(inc.severity)">{{ inc.severity }}</span></td>
            <td class="muted">{{ inc.detected }}</td>
            <td><span class="badge" :class="inc.status === 'open' ? 'critical' : 'active'">{{ inc.status === 'open' ? 'Open' : 'Resolved' }}</span></td>
          </tr>
        </tbody>
      </table>
      <div class="table-foot">{{ incidents.length }} incidents in the last 30 days</div>
    </div>

    <div class="card" style="padding:16px">
      <p class="section-title" style="margin-bottom:6px">Weekly trend</p>
      <div class="row" style="align-items:baseline;gap:8px;margin-bottom:14px">
        <span style="font-size:1.6rem;font-weight:800" :style="{ color: trendUp ? 'var(--red)' : 'var(--green)' }">
          {{ trendUp ? '+' : '' }}{{ trendPct }}%
        </span>
        <span class="muted" style="font-size:12.5px">vs. previous 7 days</span>
      </div>
      <svg width="100%" height="72" viewBox="0 0 220 72" preserveAspectRatio="none" role="img" aria-label="Weekly flagged-incident trend">
        <polyline :points="sparkPoints" fill="none" :stroke="trendUp ? 'var(--red)' : 'var(--green)'" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
        <circle v-for="(p, i) in sparkDots" :key="i" :cx="p.x" :cy="p.y" r="2.6" :fill="trendUp ? 'var(--red)' : 'var(--green)'" />
      </svg>
      <div class="row" style="justify-content:space-between;margin-top:6px">
        <span class="muted" style="font-size:11px">7 days ago</span>
        <span class="muted" style="font-size:11px">Today</span>
      </div>

      <p class="section-title" style="margin:18px 0 10px">By incident type</p>
      <div class="barchart">
        <div class="brow" v-for="t in byType" :key="t.type">
          <span class="blabel">{{ t.type }}</span>
          <svg class="btrack" width="100%" height="10" role="img" :aria-label="`${t.type}: ${t.count}`">
            <rect width="100%" height="10" rx="3" fill="var(--surface-3)" />
            <rect :width="typePct(t.count) + '%'" height="10" rx="3" fill="var(--crit)" />
          </svg>
          <span class="bval">{{ t.count }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Flame } from 'lucide-vue-next'

function seeded(seed) {
  const x = Math.sin(seed * 33.7 + 8.1) * 63498.2
  return x - Math.floor(x)
}
const companies = ['Everest Logistics', 'Blue Ridge Fuels', 'Coastal Freight Co.', 'Northgate Transport', 'Summit Haulage']
const types = ['Fuel theft', 'Route deviation', 'Tamper detected', 'Odometer anomaly', 'Unauthorized stop']
const severities = ['low', 'medium', 'high']

const incidents = Array.from({ length: 12 }, (_, i) => {
  const seed = i + 1
  const daysAgo = Math.floor(seeded(seed * 3 + 1) * 30)
  return {
    id: seed,
    company: companies[Math.floor(seeded(seed * 5 + 2) * companies.length)],
    vehicle: `Vehicle ${100 + Math.floor(seeded(seed * 7 + 3) * 80)}`,
    type: types[Math.floor(seeded(seed * 11 + 4) * types.length)],
    severity: severities[Math.floor(seeded(seed * 13 + 5) * severities.length)],
    status: seeded(seed * 17 + 6) > 0.4 ? 'open' : 'resolved',
    detected: `${daysAgo}d ago`,
  }
}).sort((a, b) => (a.status === 'open' ? -1 : 1) - (b.status === 'open' ? -1 : 1))

const openCount = incidents.filter((i) => i.status === 'open').length
const resolvedCount = incidents.filter((i) => i.status === 'resolved').length
function sevClass(s) { return s === 'high' ? 'critical' : s === 'medium' ? 'warning' : 'info' }

const byType = computed(() => types.map((t) => ({ type: t, count: incidents.filter((i) => i.type === t).length })))
const maxType = Math.max(1, ...byType.value.map((t) => t.count))
function typePct(n) { return n ? Math.max(6, (n / maxType) * 100) : 0 }

// 7-point weekly trend sparkline
const weekly = [4, 6, 5, 8, 7, 10, 9]
const trendPct = Math.round(((weekly[6] - weekly[0]) / weekly[0]) * 100)
const trendUp = trendPct >= 0
const maxW = Math.max(...weekly), minW = Math.min(...weekly)
const sparkDots = weekly.map((v, i) => ({
  x: (i / (weekly.length - 1)) * 220,
  y: 66 - ((v - minW) / Math.max(1, maxW - minW)) * 56,
}))
const sparkPoints = sparkDots.map((p) => `${p.x},${p.y}`).join(' ')
</script>

<style scoped>
.barchart { display: flex; flex-direction: column; gap: 10px; }
.brow { display: grid; grid-template-columns: 120px 1fr 28px; align-items: center; gap: 10px; }
.blabel { font-size: 12px; font-weight: 700; color: var(--muted); }
.bval { font-size: 12.5px; font-weight: 800; text-align: right; font-variant-numeric: tabular-nums; }
</style>
