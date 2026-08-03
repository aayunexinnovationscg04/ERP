<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow"><router-link to="/users" class="muted">Users</router-link> / Member access</span>
      <h1>Tabs &amp; overrides</h1>
    </div>
    <div class="row">
      <span class="muted ico" v-if="saved"><Check :size="16" /> Saved</span>
      <button class="primary ico" style="width:auto" @click="save" :disabled="saving"><Check :size="16" /> {{ saving ? 'Saving…' : 'Save overrides' }}</button>
    </div>
  </div>
  <p class="hint">Role: <span class="role-badge" :class="data.role">{{ roleLabel(data.role) }}</span> &nbsp;·&nbsp; Choose <b>Default</b> to follow the role, or override per tab for this member.</p>

  <div v-if="loading" class="card" style="padding:16px;margin-top:14px">
    <div class="skel sk-row" v-for="n in 6" :key="n"></div>
  </div>

  <div v-else class="card" style="padding:6px 0;margin-top:14px">
    <table>
      <thead><tr><th>Module / Tab</th><th>Role default</th><th>This member</th><th>Effective</th></tr></thead>
      <tbody>
        <motion.tr
          v-for="(m, idx) in modules" :key="m.key"
          :initial="{ opacity: 0, y: 4 }" :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: 0.14, delay: Math.min(idx, 10) * 0.015, ease: [0.4, 0, 0.2, 1] }"
        >
          <td>{{ m.label }} <span class="muted" style="font-size:11px">{{ m.key }}</span></td>
          <td><span class="badge ico" :class="data.role_defaults[m.key] ? 'active' : 'offline'"><component :is="data.role_defaults[m.key] ? Check : X" :size="13" /> {{ data.role_defaults[m.key] ? 'allowed' : 'denied' }}</span></td>
          <td>
            <select v-model="state[m.key]" style="width:auto">
              <option value="default">Default</option>
              <option value="allow">Grant</option>
              <option value="deny">Deny</option>
            </select>
          </td>
          <td><span class="badge ico" :class="effective(m.key) ? 'active' : 'offline'"><component :is="effective(m.key) ? Check : X" :size="13" /> {{ effective(m.key) ? 'yes' : 'no' }}</span></td>
        </motion.tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { motion } from 'motion-v'
import { Check, X } from 'lucide-vue-next'
import { getUserPerms, setUserPerms, getModules } from '../api'
import { toast } from '../toast'

const props = defineProps({ id: [String, Number] })
const modules = ref([])
const data = ref({ role: '', role_defaults: {}, overrides: {}, effective: [] })
const state = ref({})   // module -> 'default' | 'allow' | 'deny'
const loading = ref(true)
const saving = ref(false); const saved = ref(false)

const roleLabels = { admin: 'Admin', dealer: 'Dealer', manager: 'Manager', pilot: 'Pilot' }
function roleLabel(r) { return roleLabels[r] || r }

function effective(key) {
  const s = state.value[key]
  if (s === 'allow') return true
  if (s === 'deny') return false
  return !!data.value.role_defaults[key]
}

async function load() {
  try {
    ;[modules.value, data.value] = await Promise.all([getModules(), getUserPerms(props.id)])
    const st = {}
    modules.value.forEach((m) => {
      const ov = data.value.overrides[m.key]
      st[m.key] = ov === undefined ? 'default' : (ov ? 'allow' : 'deny')
    })
    state.value = st
  } finally { loading.value = false }
}
async function save() {
  saving.value = true; saved.value = false
  const overrides = {}
  modules.value.forEach((m) => {
    const s = state.value[m.key]
    overrides[m.key] = s === 'default' ? null : s === 'allow'
  })
  try {
    await setUserPerms(props.id, overrides); await load(); saved.value = true; setTimeout(() => (saved.value = false), 2500)
    toast.success('Permissions saved')
  } catch (e) {
    toast.error('Could not save permissions')
  } finally { saving.value = false }
}
onMounted(load)
</script>

<style scoped>
select { font: inherit; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 10px; border-radius: 8px; }
</style>
