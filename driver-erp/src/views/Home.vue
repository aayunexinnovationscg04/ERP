<template>
  <div v-if="loading" class="empty">Loading your truck…</div>

  <div v-else-if="!assigned" class="card empty">
    <div style="font-size:40px">🚚</div>
    <h2 style="margin:10px 0 6px">No truck assigned yet</h2>
    <p class="muted">Your dispatcher hasn't linked a vehicle to your account.<br />Once they do, it shows up here.</p>
  </div>

  <div v-else>
    <!-- status hero -->
    <div class="card hero">
      <div class="row">
        <div>
          <div class="reg">{{ v.registration_number }}</div>
          <div class="sub">{{ [v.make, v.model].filter(Boolean).join(' ') || 'Vehicle' }}</div>
        </div>
        <div class="spacer"></div>
        <div style="text-align:right">
          <span class="badge" :class="v.status">{{ v.status }}</span>
          <div style="margin-top:8px">
            <span class="badge" :class="summary.on_trip ? 'on' : 'off'">
              {{ summary.on_trip ? '● On trip' : 'Parked' }}
            </span>
          </div>
        </div>
      </div>

      <div class="chips">
        <div class="chip"><div class="l">Speed</div><div class="v">{{ fmt(latest?.speed_kmph) }} <small class="muted">km/h</small></div></div>
        <div class="chip"><div class="l">Distance today</div><div class="v">{{ summary.distance_today_km ?? 0 }} <small class="muted">km</small></div></div>
        <div class="chip"><div class="l">Fuel cap</div><div class="v">{{ latest?.lock_active ? '🔒 Locked' : '🔓 Open' }}</div></div>
        <div class="chip"><div class="l">GPS</div><div class="v">{{ latest?.has_gps_fix ? ('★ ' + (latest?.satellites ?? 0)) : 'No fix' }}</div></div>
      </div>
    </div>

    <div v-if="summary.open_alerts" class="card item" style="border-color:var(--crit)">
      <div><div class="t">🔔 {{ summary.open_alerts }} open alert{{ summary.open_alerts > 1 ? 's' : '' }}</div>
        <div class="d">Tap the Alerts tab to review</div></div>
      <router-link to="/alerts" class="badge critical" style="align-self:center">View</router-link>
    </div>

    <div class="section-title">Live location &amp; today's route</div>
    <FleetMap :markers="markers" :track="track" />

    <div class="muted" style="font-size:12px; margin-top:12px; text-align:center">
      Last update: {{ latest ? new Date(latest.received_at).toLocaleString() : '—' }} · refreshes every 20s
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import FleetMap from '../components/FleetMap.vue'
import { getSummary, getMyTrack } from '../api'

const loading = ref(true)
const summary = ref({})
const track = ref([])
let timer = null

const assigned = computed(() => summary.value.assigned)
const v = computed(() => summary.value.vehicle || {})
const latest = computed(() => summary.value.latest)

const markers = computed(() => {
  const l = latest.value
  if (!l || !l.has_gps_fix) return []
  return [{ id: v.value.id, lat: l.latitude, lng: l.longitude, label: v.value.registration_number, status: v.value.status }]
})

function fmt(n) { return n == null ? '—' : Math.round(n) }

async function load() {
  try {
    summary.value = await getSummary()
    if (summary.value.assigned) {
      const pts = await getMyTrack(500)
      track.value = pts.filter((p) => p.has_gps_fix).map((p) => [p.latitude, p.longitude])
    }
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}

onMounted(() => { load(); timer = setInterval(load, 20000) })
onBeforeUnmount(() => clearInterval(timer))
</script>
