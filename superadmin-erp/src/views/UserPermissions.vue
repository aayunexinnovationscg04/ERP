<template>
  <div class="topbar">
    <h1><router-link to="/users" class="muted">Users</router-link> / member access</h1>
    <div class="row">
      <span class="muted ico" v-if="saved"><Check :size="16" /> Saved</span>
      <button class="primary ico" @click="save" :disabled="saving"><Check :size="16" /> {{ saving ? 'Saving…' : 'Save overrides' }}</button>
    </div>
  </div>
  <p class="muted" style="margin-top:-8px">Role: <b>{{ data.role }}</b>. Choose <b>Default</b> to follow the role, or override per tab for this member.</p>

  <div v-if="loading" class="card" style="padding:16px;margin-top:14px">
    <div class="skel sk-row" v-for="n in 6" :key="n"></div>
  </div>

  <div v-else class="card" style="padding:6px 0;margin-top:14px">
    <table>
      <thead><tr><th>Module / Tab</th><th>Role default</th><th>This member</th><th>Effective</th></tr></thead>
      <tbody>
        <tr v-for="m in modules" :key="m.key">
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
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Check, X } from 'lucide-vue-next'
import { getUserPerms, setUserPerms, getModules } from '../api'

const props = defineProps({ id: [String, Number] })
const modules = ref([])
const data = ref({ role: '', role_defaults: {}, overrides: {}, effective: [] })
const state = ref({})   // module -> 'default' | 'allow' | 'deny'
const loading = ref(true)
const saving = ref(false); const saved = ref(false)

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
  try { await setUserPerms(props.id, overrides); await load(); saved.value = true; setTimeout(() => (saved.value = false), 2500) }
  finally { saving.value = false }
}
onMounted(load)
</script>

<style scoped>
select { font: inherit; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 10px; border-radius: 8px; }
</style>
