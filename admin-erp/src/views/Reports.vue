<template>
  <PageHeader :icon="ChartLine" title="Global Reports" description="Platform-wide usage over the last 7 days: sign-ins, sessions and API traffic." />

  <div class="notice info">
    <FlaskConical :size="16" />
    <span><strong>Sample data</strong> <span class="muted">· live usage analytics not connected yet</span></span>
  </div>

  <div class="stats">
    <StatCard label="Sign-ins (7 days)" :value="totals.logins.toLocaleString()" :icon="LogIn" tone="navy" />
    <StatCard label="Peak active sessions" :value="totals.sessions.toLocaleString()" :icon="Users" tone="teal" />
    <StatCard label="API calls (7 days)" :value="totals.apiCalls.toLocaleString()" :icon="Activity" tone="info" />
    <StatCard label="Avg. API latency" :value="totals.avgLatency + ' ms'" :icon="Gauge" tone="amber" />
  </div>

  <section class="card">
    <div class="card-head"><h2>API calls, last 7 days</h2></div>
    <div class="card-body">
      <div class="chart" @mouseleave="hover = null">
        <svg viewBox="0 0 700 200" preserveAspectRatio="none" role="img" aria-label="API calls per day over the last 7 days" class="chart-svg">
          <line v-for="g in 4" :key="g" x1="0" x2="700" :y1="g * 45 - 5" :y2="g * 45 - 5" stroke="var(--border)" stroke-width="1" vector-effect="non-scaling-stroke" />
          <polyline :points="linePoints" fill="none" stroke="var(--info)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke" />
          <line v-if="hover !== null" :x1="dots[hover].x" :x2="dots[hover].x" y1="0" y2="200" stroke="var(--border-strong)" stroke-width="1" vector-effect="non-scaling-stroke" />
        </svg>
        <span
          v-for="(p, i) in dots" :key="i" class="pt" :class="{ on: hover === i }"
          :style="{ left: (p.x / 700 * 100) + '%', top: (p.y / 200 * 100) + '%' }"
        ></span>
        <div class="hit">
          <span v-for="(d, i) in days" :key="d" :style="{ left: ((dots[i].x - 55) / 700 * 100) + '%', width: (110 / 700 * 100) + '%' }" @mouseenter="hover = i" @focus="hover = i" @blur="hover = null" tabindex="0" :aria-label="`${d}: ${daily.apiCalls[i].toLocaleString()} API calls`"></span>
        </div>
        <div v-if="hover !== null" class="tip" :style="{ left: (dots[hover].x / 700 * 100) + '%' }">
          <strong>{{ days[hover] }}</strong>{{ daily.apiCalls[hover].toLocaleString() }} calls
        </div>
      </div>
      <div class="x-labels"><span v-for="d in days" :key="d">{{ d }}</span></div>
    </div>
  </section>

  <section class="card mt">
    <div class="card-head"><h2>Daily breakdown</h2></div>
    <div class="table-wrap">
      <table class="table stack cols-3">
        <thead><tr><th>Day</th><th class="t-right">Sign-ins</th><th class="t-right">Active sessions</th><th class="t-right">API calls</th></tr></thead>
        <tbody>
          <tr v-for="(d, i) in days" :key="d">
            <td class="cell-head"><span class="t-primary">{{ d }}</span></td>
            <td data-label="Sign-ins" class="t-right num">{{ daily.logins[i] }}</td>
            <td data-label="Active sessions" class="t-right num">{{ daily.sessions[i] }}</td>
            <td data-label="API calls" class="t-right num">{{ daily.apiCalls[i].toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { ChartLine, LogIn, Users, Activity, Gauge, FlaskConical } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'

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

// y-axis starts at zero so day-to-day differences aren't exaggerated
const maxCalls = Math.max(...daily.apiCalls) * 1.1
const dots = daily.apiCalls.map((v, i) => ({
  x: 20 + (i / (daily.apiCalls.length - 1)) * 660,
  y: 190 - (v / maxCalls) * 180,
}))
const linePoints = dots.map((p) => `${p.x},${p.y}`).join(' ')
const hover = ref(null)
</script>

<style scoped>
.chart { position: relative; height: 220px; }
.chart-svg { width: 100%; height: 100%; display: block; overflow: visible; }
.pt {
  position: absolute; width: 10px; height: 10px; margin: -5px 0 0 -5px; border-radius: 50%;
  background: var(--info); box-shadow: 0 0 0 2px var(--surface); pointer-events: none;
}
.pt.on { width: 12px; height: 12px; margin: -6px 0 0 -6px; }
.hit { position: absolute; inset: 0; overflow: hidden; }
.hit span { position: absolute; top: 0; bottom: 0; outline: none; }
.tip {
  position: absolute; top: -6px; transform: translateX(-50%); pointer-events: none; white-space: nowrap;
  background: var(--ink-strong); color: var(--surface); border-radius: var(--radius-xs);
  padding: 6px 10px; font-size: .75rem; font-weight: 600; display: flex; gap: 8px; box-shadow: var(--shadow-md);
}
.x-labels { display: flex; justify-content: space-between; padding: 8px calc(20 / 700 * 100%) 0; font-size: .75rem; color: var(--muted); }
.x-labels span { width: 0; display: flex; justify-content: center; white-space: nowrap; }
</style>
