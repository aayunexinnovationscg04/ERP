<template>
  <h1>Alerts</h1>
  <div class="muted" style="margin-bottom:14px">Safety &amp; security notices for your truck</div>

  <div v-if="loading">
    <div v-for="n in 4" :key="n" class="skel sk-item"></div>
  </div>
  <div v-else-if="!alerts.length" class="card empty">
    <CircleCheck :size="30" :stroke-width="1.75" style="color:var(--green)" />
    <div style="margin-top:8px">No alerts. All clear.</div>
  </div>

  <div v-else>
    <div v-for="a in alerts" :key="a.id" class="card item">
      <div>
        <div class="t">{{ a.title || a.type }}</div>
        <div class="d">{{ a.message }}</div>
        <div class="d">{{ when(a.created_at) }}</div>
      </div>
      <div style="text-align:right; align-self:flex-start">
        <span class="badge" :class="a.severity">{{ a.severity }}</span>
        <div class="d" style="margin-top:6px">{{ a.status }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { CircleCheck } from 'lucide-vue-next'
import { getMyAlerts } from '../api'

const loading = ref(true)
const alerts = ref([])

function when(s) { return s ? new Date(s).toLocaleString() : '—' }

onMounted(async () => {
  try { alerts.value = await getMyAlerts() } catch (e) { /* ignore */ }
  finally { loading.value = false }
})
</script>
