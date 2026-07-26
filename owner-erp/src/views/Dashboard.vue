<template>
  <div class="topbar">
    <h1>Dashboard</h1>
    <span class="muted">{{ auth.user?.company?.name }} · live</span>
  </div>

  <div v-if="loading">
    <div class="kpis">
      <div v-for="n in 6" :key="n" class="skel sk-chip"></div>
    </div>
    <div class="grid-2">
      <div>
        <p class="section-title">Live fleet map</p>
        <div class="skel sk-map"></div>
      </div>
      <div>
        <p class="section-title">Recent alerts</p>
        <div class="skel sk-row" v-for="n in 5" :key="n"></div>
      </div>
    </div>
  </div>

  <template v-else>
    <div class="kpis">
      <div class="card kpi"><div class="n">{{ s.vehicles_total == null ? '–' : disp.vehicles_total }}</div><div class="l">Trucks</div></div>
      <div class="card kpi"><div class="n" style="color:var(--green)">{{ s.active == null ? '–' : disp.active }}</div><div class="l">Active</div></div>
      <div class="card kpi"><div class="n" style="color:var(--amber)">{{ s.idle == null ? '–' : disp.idle }}</div><div class="l">Idle</div></div>
      <div class="card kpi"><div class="n" style="color:#94a3b8">{{ s.offline == null ? '–' : disp.offline }}</div><div class="l">Offline</div></div>
      <div class="card kpi"><div class="n" style="color:var(--crit)">{{ s.open_alerts == null ? '–' : disp.open_alerts }}</div><div class="l">Open alerts</div></div>
      <div class="card kpi"><div class="n">{{ s.distance_today_km == null ? '–' : disp.distance_today_km }}</div><div class="l">km today</div></div>
    </div>

    <div class="grid-2">
      <div>
        <p class="section-title">Live fleet map</p>
        <FleetMap :markers="markers" @select="goVehicle" />
      </div>
      <div>
        <p class="section-title">Recent alerts</p>
        <div class="card" style="padding:6px 0">
          <table>
            <tbody>
              <tr v-for="a in alerts" :key="a.id">
                <td><span class="badge" :class="a.severity">{{ a.severity }}</span></td>
                <td>{{ a.title }}<div class="muted" style="font-size:12px">{{ a.vehicle_reg || a.device_id }}</div></td>
              </tr>
              <tr v-if="!alerts.length">
                <td class="muted ico" style="padding:16px"><CircleCheck :size="16" style="color:var(--green)" /> All clear — no open alerts</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </template>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { CircleCheck } from 'lucide-vue-next'
import { auth } from '../auth'
import { getSummary, getVehicles, getAlerts } from '../api'
import FleetMap from '../components/FleetMap.vue'

const router = useRouter()
const loading = ref(true)
const s = ref({})
const markers = ref([])
const alerts = ref([])
let timer

// KPI count-up (easeOutCubic, ~600ms) — first load only, honours reduced-motion
const KPI_KEYS = ['vehicles_total', 'active', 'idle', 'offline', 'open_alerts', 'distance_today_km']
const disp = reactive(Object.fromEntries(KPI_KEYS.map((k) => [k, 0])))
let animated = false
const prefersReduced = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches : false

function countUp(key, target) {
  const isFloat = !Number.isInteger(target)
  const start = performance.now()
  function frame(now) {
    const t = Math.min(1, (now - start) / 600)
    const e = 1 - Math.pow(1 - t, 3)
    const v = target * e
    disp[key] = isFloat ? Math.round(v * 10) / 10 : Math.round(v)
    if (t < 1) requestAnimationFrame(frame)
    else disp[key] = target
  }
  requestAnimationFrame(frame)
}

function applyKpis(summary) {
  KPI_KEYS.forEach((k) => {
    const raw = summary?.[k]
    if (raw == null || isNaN(Number(raw))) { disp[k] = raw; return }
    const target = Number(raw)
    if (!animated && !prefersReduced) countUp(k, target)
    else disp[k] = target
  })
  animated = true
}

async function load() {
  try {
    const [summary, vehicles, al] = await Promise.all([
      getSummary(), getVehicles(), getAlerts({ status: 'open' }),
    ])
    s.value = summary
    applyKpis(summary)
    markers.value = vehicles
      .filter((v) => v.latest && v.latest.has_gps_fix)
      .map((v) => ({ id: v.id, lat: v.latest.latitude, lng: v.latest.longitude, label: v.registration_number, status: v.status }))
    alerts.value = al.slice(0, 8)
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
function goVehicle(id) { router.push(`/vehicles/${id}`) }

onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>
