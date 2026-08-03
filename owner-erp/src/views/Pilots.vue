<template>
  <div class="topbar">
    <h1>Pilots</h1>
    <span class="muted">{{ driverCount }} driver(s)</span>
  </div>

  <div v-if="loading" class="pilot-grid">
    <div class="skel sk-box" v-for="n in 4" :key="n"></div>
  </div>

  <div v-else class="pilot-grid">
    <button type="button" class="pilot-box" v-for="v in vehicles" :key="v.id"
            :disabled="!v.active_driver" :title="v.active_driver ? 'View pilot' : 'No pilot assigned'"
            @click="v.active_driver && $router.push(`/pilots/${v.active_driver.id}`)">
      <div class="pb-avatar"><UserRound :size="19" /></div>
      <div class="pb-name">{{ v.local_name }}</div>
      <div class="muted pb-reg"><Truck :size="12" class="pb-reg-ic" />{{ v.registration_number }}</div>
      <div class="pb-pilot" :class="{ muted: !v.active_driver }">
        <template v-if="v.active_driver"><UserRound :size="13" class="pilot-ic" />{{ v.active_driver.name }}</template>
        <template v-else>No pilot assigned</template>
      </div>
    </button>

    <p v-if="!vehicles.length" class="muted">No vehicles yet.</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { UserRound, Truck } from 'lucide-vue-next'
import { getVehicles } from '../api'

const vehicles = ref([])
const loading = ref(true)
const driverCount = computed(() => vehicles.value.filter((v) => v.active_driver).length)

async function load() {
  try { vehicles.value = await getVehicles() }
  catch (e) { /* keep last good data */ }
  finally { loading.value = false }
}
onMounted(load)
</script>

<style scoped>
.pilot-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 220px)); gap: 18px; }
.sk-box { height: 170px; border-radius: var(--radius); }

.pilot-box {
  text-align: center; background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); box-shadow: var(--shadow-sm); padding: 26px 18px;
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  transition: box-shadow var(--dur) var(--ease), transform var(--dur) var(--ease), border-color var(--dur) var(--ease);
}
.pilot-box:not(:disabled):hover { box-shadow: var(--shadow-md); border-color: var(--brand); transform: translateY(-2px); }
.pilot-box:not(:disabled):active { transform: translateY(0) scale(.99); }
.pilot-box:disabled { cursor: default; opacity: .7; }

.pb-avatar {
  width: 40px; height: 40px; border-radius: 50%; display: grid; place-items: center;
  background: var(--surface-2); color: var(--muted);
}
.pb-name { font-weight: 700; font-size: 15.5px; margin-top: 2px; }
.pb-reg { font-size: 12px; margin-top: -6px; display: flex; align-items: center; gap: 5px; }
.pb-reg-ic { flex: none; }
.pb-pilot {
  display: flex; align-items: center; gap: 5px; font-size: 12.5px; font-weight: 600;
  margin-top: 4px; padding-top: 8px; border-top: 1px solid var(--border); width: 100%; justify-content: center;
}
.pilot-ic { color: var(--brand); flex: none; }
.pb-pilot.muted .pilot-ic { display: none; }
</style>
