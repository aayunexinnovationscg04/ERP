<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Security &amp; Analytics</span>
      <h1 class="ico"><ChartLine :size="20" /> Global Reports</h1>
    </div>
  </div>
  <p class="hint">Platform-wide usage over the last 7 days. Illustrative sample pending a dedicated usage-analytics pipeline.</p>

  <div class="stats">
    <div class="card stat" style="--stat-color:#8b5cf6;--stat-color-soft:rgba(139,92,246,.16)">
      <span class="stat-icon"><LogIn :size="16" /></span>
      <div class="n">{{ totals.logins.toLocaleString() }}</div><div class="l">Logins (7d)</div>
    </div>
    <div class="card stat" style="--stat-color:#2dd4bf;--stat-color-soft:rgba(45,212,191,.16)">
      <span class="stat-icon"><Users :size="16" /></span>
      <div class="n">{{ totals.sessions.toLocaleString() }}</div><div class="l">Active sessions (peak)</div>
    </div>
    <div class="card stat" style="--stat-color:#38bdf8;--stat-color-soft:rgba(56,189,248,.16)">
      <span class="stat-icon"><Activity :size="16" /></span>
      <div class="n">{{ totals.apiCalls.toLocaleString() }}</div><div class="l">API calls (7d)</div>
    </div>
    <div class="card stat" style="--stat-color:#f59e0b;--stat-color-soft:rgba(245,158,11,.16)">
      <span class="stat-icon"><Gauge :size="16" /></span>
      <div class="n">{{ totals.avgLatency }} ms</div><div class="l">Avg. API latency</div>
    </div>
  </div>

  <div class="card" style="padding:16px;margin-top:20px">
    <p class="section-title" style="margin-bottom:14px">API calls, last 7 days</p>
    <svg width="100%" height="180" viewBox="0 0 700 180" preserveAspectRatio="none" role="img" aria-label="API calls over the last 7 days">
      <line v-for="g in 4" :key="g" :x1="0" :x2="700" :y1="g * 40" :y2="g * 40" stroke="var(--border)" stroke-width="1" />
      <polygon :points="areaPoints" fill="var(--brand-soft)" />
      <polyline :points="linePoints" fill="none" stroke="var(--brand)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
      <circle v-for="(p, i) in dots" :key="i" :cx="p.x" :cy="p.y" r="3.2" fill="var(--brand)" />
    </svg>
    <div class="row" style="justify-content:space-between;margin-top:4px">
      <span class="muted" style="font-size:11px" v-for="d in days" :key="d">{{ d }}</span>
    </div>
  </div>

  <div class="card" style="padding:6px 0;margin-top:18px">
    <table>
      <thead><tr><th>Day</th><th>Logins</th><th>Active sessions</th><th>API calls</th></tr></thead>
      <tbody>
        <tr v-for="(d, i) in days" :key="d">
          <td>{{ d }}</td>
          <td class="num">{{ daily.logins[i] }}</td>
          <td class="num">{{ daily.sessions[i] }}</td>
          <td class="num">{{ daily.apiCalls[i].toLocaleString() }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ChartLine, LogIn, Users, Activity, Gauge } from 'lucide-vue-next'

function seeded(seed) {
  const x = Math.sin(seed * 45.9 + 12.3) * 51231.7
  return x - Math.floor(x)
}

const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const daily = {
  logins: days.map((_, i) => 30 + Math.floor(seeded(i * 3 + 1) * 90)),
  sessions: days.map((_, i) => 10 + Math.floor(seeded(i * 5 + 2) * 40)),
  apiCalls: days.map((_, i) => 2000 + Math.floor(seeded(i * 7 + 3) * 6000)),
}
const totals = {
  logins: daily.logins.reduce((a, b) => a + b, 0),
  sessions: Math.max(...daily.sessions),
  apiCalls: daily.apiCalls.reduce((a, b) => a + b, 0),
  avgLatency: 60 + Math.floor(seeded(99) * 90),
}

const maxCalls = Math.max(...daily.apiCalls)
const minCalls = Math.min(...daily.apiCalls)
const dots = daily.apiCalls.map((v, i) => ({
  x: (i / (daily.apiCalls.length - 1)) * 700,
  y: 160 - ((v - minCalls) / Math.max(1, maxCalls - minCalls)) * 140,
}))
const linePoints = dots.map((p) => `${p.x},${p.y}`).join(' ')
const areaPoints = `0,180 ${linePoints} 700,180`
</script>
