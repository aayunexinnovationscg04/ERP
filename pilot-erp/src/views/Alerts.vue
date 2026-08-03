<template>
  <h1>Alerts</h1>
  <div class="muted" style="margin-bottom:14px">Safety &amp; security notices for your truck</div>

  <div v-if="loading">
    <div v-for="n in 4" :key="n" class="skel sk-item"></div>
  </div>
  <div v-else-if="!alerts.length" class="card empty">
    <CircleCheck :size="34" :stroke-width="1.75" style="color:var(--green)" />
    <div style="margin-top:8px">No alerts. All clear.</div>
  </div>

  <div v-else>
    <motion.div v-for="(a, i) in alerts" :key="a.id" class="card item"
      :class="'sev-' + (severityClass(a.severity) || 'info')"
      :initial="{ opacity: 0, y: reduced ? 0 : 8 }" :animate="{ opacity: 1, y: 0 }"
      :transition="{ duration: reduced ? 0 : 0.22, delay: reduced ? 0 : Math.min(i, 8) * 0.03, ease: EASE }">
      <div class="item-row">
        <span class="item-ic" :class="severityClass(a.severity) || 'info'">
          <component :is="severityIcon(a.severity)" :size="17" :stroke-width="2.25" />
        </span>
        <div>
          <div class="t">{{ a.title || a.type }}</div>
          <div class="d">{{ a.message }}</div>
          <div class="d">{{ when(a.created_at) }}</div>
        </div>
      </div>
      <div style="text-align:right; align-self:flex-start">
        <span class="badge" :class="a.severity"><span class="dot"></span>{{ a.severity }}</span>
        <div class="d" style="margin-top:6px">{{ a.status }}</div>
      </div>
    </motion.div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { motion } from 'motion-v'
import { CircleCheck, TriangleAlert, ShieldAlert, Info } from 'lucide-vue-next'
import { getMyAlerts } from '../api'
import { usePrefersReducedMotion, EASE } from '../motion'

const reduced = usePrefersReducedMotion()
const loading = ref(true)
const alerts = ref([])

function when(s) { return s ? new Date(s).toLocaleString() : '—' }
function severityClass(sev) {
  if (sev === 'critical') return 'critical'
  if (sev === 'warning') return 'warning'
  return ''
}
// severity now drives the icon glyph too, not just its color — so a critical
// alert and an informational one look genuinely different at a glance, the
// same fix philosophy applied to the trips list
function severityIcon(sev) {
  if (sev === 'critical') return ShieldAlert
  if (sev === 'warning') return TriangleAlert
  return Info
}

onMounted(async () => {
  try { alerts.value = await getMyAlerts() } catch (e) { /* ignore */ }
  finally { loading.value = false }
})
</script>
