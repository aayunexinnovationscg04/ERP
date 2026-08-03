<template>
  <div class="topbar">
    <h1>Fuel</h1>
    <span class="muted">{{ vehicles.length }} vehicle(s)</span>
  </div>

  <div v-if="loading" class="fuel-grid">
    <div class="skel sk-box" v-for="n in 4" :key="n"></div>
  </div>

  <div v-else class="fuel-grid">
    <button type="button" class="fuel-box" v-for="v in vehicles" :key="v.id" @click="$router.push(`/fuel/${v.id}`)">
      <div class="fb-top">
        <span class="dot" :class="freshness(v)"></span>
        <span class="fb-name">{{ v.local_name }}</span>
      </div>
      <div class="muted fb-reg">{{ v.registration_number }}</div>
      <div class="fb-level">
        <Fuel :size="15" class="fb-ic" />
        <b>{{ fmt(v.latest?.total_litres) }}</b><span class="muted">L</span>
      </div>
      <div class="fb-bar"><div class="fb-bar-fill" :style="{ width: pct(v) + '%' }"></div></div>
      <div class="muted fb-cap">{{ v.tank_capacity_litres ? pct(v) + '% of ' + v.tank_capacity_litres + ' L tank' : 'Tank capacity not set' }}</div>
    </button>

    <p v-if="!vehicles.length" class="muted">No vehicles yet.</p>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { Fuel } from 'lucide-vue-next'
import { getVehicles } from '../api'
import { freshness, fmt } from '../util'

const vehicles = ref([])
const loading = ref(true)
let timer

function pct(v) {
  if (!v.tank_capacity_litres || v.latest?.total_litres == null) return 0
  return Math.max(0, Math.min(100, Math.round((v.latest.total_litres / v.tank_capacity_litres) * 100)))
}

async function load() {
  try { vehicles.value = await getVehicles() }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(() => { load(); timer = setInterval(load, 15000) })
onBeforeUnmount(() => clearInterval(timer))
</script>

<style scoped>
/* Fixed-ish tile width (not 1fr) so a single vehicle doesn't stretch into one
   giant box — each tile stays a compact card and the grid just adds more of
   them as vehicles are added. */
.fuel-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 240px)); gap: 14px; }
.sk-box { height: 128px; border-radius: var(--radius); }

.fuel-box {
  text-align: left; background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); box-shadow: var(--shadow-sm); padding: 18px 20px;
  display: flex; flex-direction: column; gap: 3px;
  transition: box-shadow var(--dur) var(--ease), transform var(--dur) var(--ease), border-color var(--dur) var(--ease);
}
.fuel-box:hover { box-shadow: var(--shadow-md); border-color: var(--brand); transform: translateY(-2px); }
.fuel-box:active { transform: translateY(0) scale(.99); }

.fb-top { display: flex; align-items: center; gap: 0; }
.fb-name { font-weight: 700; font-size: 15.5px; }
.fb-reg { font-size: 12px; margin-bottom: 10px; }

.fb-level { display: flex; align-items: baseline; gap: 5px; }
.fb-ic { color: var(--brand); flex: none; align-self: center; margin-right: 2px; }
.fb-level b { font-size: 22px; font-weight: 800; letter-spacing: -.01em; }
.fb-level .muted { font-size: 12.5px; }

.fb-bar { height: 6px; border-radius: 999px; background: var(--surface-2); overflow: hidden; margin-top: 8px; }
.fb-bar-fill { height: 100%; background: var(--accent-grad); border-radius: 999px; }
.fb-cap { font-size: 11.5px; margin-top: 5px; }
</style>
