<template>
  <h1>My Trips</h1>
  <div class="muted" style="margin-bottom:14px">Recent journeys for your truck</div>

  <div v-if="loading">
    <div v-for="n in 5" :key="n" class="skel sk-item"></div>
  </div>
  <div v-else-if="!trips.length" class="card empty">
    <Route :size="34" :stroke-width="1.5" style="color:var(--muted)" />
    <div style="margin-top:8px">No trips recorded yet.</div>
  </div>

  <div v-else>
    <motion.div v-for="(t, i) in trips" :key="t.id" class="card item"
      :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }"
      :transition="{ duration: reduced ? 0 : 0.22, delay: reduced ? 0 : Math.min(i, 8) * 0.03, ease: EASE }">
      <div class="item-row">
        <span class="item-ic" :class="{ on: t.status === 'active' }">
          <component :is="t.status === 'active' ? Navigation : CheckCheck" :size="17" />
        </span>
        <div>
          <div class="t">
            <span class="badge" :class="t.status === 'active' ? 'on' : 'info'">
              <span class="dot"></span>{{ t.status === 'active' ? 'Active' : 'Completed' }}
            </span>
          </div>
          <div class="d">{{ when(t.started_at) }} → {{ t.ended_at ? when(t.ended_at) : 'now' }}</div>
        </div>
      </div>
      <div style="text-align:right">
        <div class="t">{{ round(t.distance_km) }} km</div>
        <div class="d">max {{ round(t.max_speed_kmph) }} · avg {{ round(t.avg_speed_kmph) }} km/h</div>
      </div>
    </motion.div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { motion } from 'motion-v'
import { Route, Navigation, CheckCheck } from 'lucide-vue-next'
import { getMyTrips } from '../api'
import { usePrefersReducedMotion, EASE } from '../motion'

const reduced = usePrefersReducedMotion()
const loading = ref(true)
const trips = ref([])

function round(n) { return Math.round((n || 0) * 10) / 10 }
function when(s) { return s ? new Date(s).toLocaleString() : '—' }

onMounted(async () => {
  try { trips.value = await getMyTrips() } catch (e) { /* ignore */ }
  finally { loading.value = false }
})
</script>
