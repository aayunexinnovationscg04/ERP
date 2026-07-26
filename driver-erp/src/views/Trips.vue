<template>
  <h1>My Trips</h1>
  <div class="muted" style="margin-bottom:14px">Recent journeys for your truck</div>

  <div v-if="loading" class="empty">Loading…</div>
  <div v-else-if="!trips.length" class="card empty">No trips recorded yet.</div>

  <div v-else>
    <div v-for="t in trips" :key="t.id" class="card item">
      <div>
        <div class="t">
          <span class="badge" :class="t.status === 'active' ? 'on' : 'info'">
            {{ t.status === 'active' ? '● Active' : 'Completed' }}
          </span>
        </div>
        <div class="d">{{ when(t.started_at) }} → {{ t.ended_at ? when(t.ended_at) : 'now' }}</div>
      </div>
      <div style="text-align:right">
        <div class="t">{{ round(t.distance_km) }} km</div>
        <div class="d">max {{ round(t.max_speed_kmph) }} · avg {{ round(t.avg_speed_kmph) }} km/h</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMyTrips } from '../api'

const loading = ref(true)
const trips = ref([])

function round(n) { return Math.round((n || 0) * 10) / 10 }
function when(s) { return s ? new Date(s).toLocaleString() : '—' }

onMounted(async () => {
  try { trips.value = await getMyTrips() } catch (e) { /* ignore */ }
  finally { loading.value = false }
})
</script>
