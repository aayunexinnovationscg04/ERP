<template>
  <div class="topbar">
    <h1>Pilots</h1>
    <span class="muted">{{ pilotCount }} pilot(s)</span>
  </div>

  <div v-if="loading" class="pilot-grid">
    <div class="skel sk-box" v-for="n in 4" :key="n"></div>
  </div>

  <div v-else class="pilot-grid">
    <motion.button type="button" class="pilot-box" v-for="(v, i) in vehicles" :key="v.id"
            :disabled="!v.active_pilot" :title="v.active_pilot ? 'View pilot' : 'No pilot assigned'"
            :initial="{ opacity: 0, y: 10 }" :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: .22, delay: Math.min(i, 12) * .03, ease: [.4, 0, .2, 1] }"
            :while-hover="v.active_pilot ? { y: -3 } : {}" :while-tap="v.active_pilot ? { scale: .98 } : {}"
            @click="v.active_pilot && $router.push(`/pilots/${v.active_pilot.id}`)">
      <div class="pb-avatar" :class="{ empty: !v.active_pilot }">
        <component :is="v.active_pilot ? UserRound : UserRoundX" :size="20" class="icon-lg" />
      </div>
      <div class="pb-name">{{ v.local_name }}</div>
      <div class="muted pb-reg"><Truck :size="12" class="pb-reg-ic" />{{ v.registration_number }}</div>
      <div class="pb-pilot" :class="{ muted: !v.active_pilot }">
        <template v-if="v.active_pilot"><UserRound :size="13" class="pilot-ic" />{{ v.active_pilot.name }}</template>
        <template v-else>No pilot assigned</template>
      </div>
    </motion.button>

    <p v-if="!vehicles.length" class="muted">No vehicles yet.</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { UserRound, UserRoundX, Truck } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { getVehicles } from '../api'

const vehicles = ref([])
const loading = ref(true)
const pilotCount = computed(() => vehicles.value.filter((v) => v.active_pilot).length)

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
.pilot-box:not(:disabled):hover { box-shadow: 0 10px 26px rgba(45,212,191,.2), var(--shadow-md); border-color: var(--teal); transform: translateY(-2px); }
.pilot-box:not(:disabled):active { transform: translateY(0) scale(.99); }
.pilot-box:disabled { cursor: default; opacity: .6; }

.pb-avatar {
  width: 44px; height: 44px; border-radius: 50%; display: grid; place-items: center;
  background: var(--teal-soft); color: var(--teal);
  transition: background var(--dur) var(--ease), color var(--dur) var(--ease);
}
.pb-avatar.empty { background: var(--gray-soft); color: var(--gray); }
.pb-name { font-weight: 700; font-size: 15.5px; margin-top: 2px; color: var(--ink-strong); }
.pb-reg { font-size: 12px; margin-top: -6px; display: flex; align-items: center; gap: 5px; }
.pb-reg-ic { flex: none; }
.pb-pilot {
  display: flex; align-items: center; gap: 5px; font-size: 12.5px; font-weight: 600;
  margin-top: 4px; padding-top: 8px; border-top: 1px solid var(--border); width: 100%; justify-content: center;
}
.pilot-ic { color: var(--teal); flex: none; }
.pb-pilot.muted .pilot-ic { display: none; }
</style>
