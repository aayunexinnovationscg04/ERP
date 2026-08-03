<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / Access Control</span>
      <h1>Role Management</h1>
    </div>
    <div class="row">
      <span class="muted ico" v-if="saved"><Check :size="16" /> Saved</span>
      <button class="primary ico" style="width:auto" @click="save" :disabled="saving"><Check :size="16" /> {{ saving ? 'Saving…' : 'Save changes' }}</button>
    </div>
  </div>
  <p class="hint">Global default tabs each role can access. Admin is always all-access. Per-user exceptions are set on the user's page.</p>

  <div class="chiprow" v-if="!loading">
    <div class="chip"><span class="chip-n num">{{ editableRoles.length }}</span><span class="chip-l">Editable roles</span></div>
    <div class="chip"><span class="chip-n num">{{ modules.length }}</span><span class="chip-l">Modules / tabs</span></div>
    <div class="chip"><span class="chip-n num">{{ groups.length }}</span><span class="chip-l">Module groups</span></div>
  </div>

  <div v-if="loading" class="card" style="padding:16px;margin-top:14px">
    <div class="skel sk-row" v-for="n in 7" :key="n"></div>
  </div>

  <div v-else class="card" style="padding:6px 0;margin-top:14px">
    <table>
      <thead>
        <tr>
          <th>Module / Tab</th>
          <th v-for="r in editableRoles" :key="r" style="text-align:center">{{ roleLabel(r) }}</th>
          <th style="text-align:center" class="muted">Admin</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="g in groups" :key="g">
          <tr class="group-row"><td :colspan="editableRoles.length + 2">{{ g }}</td></tr>
          <motion.tr
            v-for="(m, idx) in modulesByGroup[g]" :key="m.key"
            :initial="{ opacity: 0, y: 4 }" :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: 0.14, delay: Math.min(idx, 8) * 0.015, ease: [0.4, 0, 0.2, 1] }"
          >
            <td>{{ m.label }} <span class="muted" style="font-size:11px">{{ m.key }}</span></td>
            <td v-for="r in editableRoles" :key="r" style="text-align:center">
              <MatrixCheckbox v-model="matrix[r][m.key]" />
            </td>
            <td style="text-align:center"><MatrixCheckbox :model-value="true" disabled /></td>
          </motion.tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { motion } from 'motion-v'
import { Check } from 'lucide-vue-next'
import { getRoles, setRoles } from '../api'
import { toast } from '../toast'
import MatrixCheckbox from '../components/MatrixCheckbox.vue'

const modules = ref([]); const matrix = ref({})
const loading = ref(true)
const saving = ref(false); const saved = ref(false)
const editableRoles = ['dealer', 'manager', 'pilot']
const roleLabels = { dealer: 'Dealer', manager: 'Manager', pilot: 'Pilot' }
function roleLabel(r) { return roleLabels[r] || r }

const groups = computed(() => [...new Set(modules.value.map((m) => m.group))])
const modulesByGroup = computed(() => {
  const o = {}; modules.value.forEach((m) => { (o[m.group] ||= []).push(m) }); return o
})

async function load() {
  try {
    const d = await getRoles()
    modules.value = d.modules
    // ensure every editable role has an entry for every module key
    const m = {}
    editableRoles.forEach((r) => {
      m[r] = {}; modules.value.forEach((mod) => { m[r][mod.key] = !!d.matrix[r]?.[mod.key] })
    })
    matrix.value = m
  } finally { loading.value = false }
}
async function save() {
  saving.value = true; saved.value = false
  try {
    await setRoles(matrix.value); saved.value = true; setTimeout(() => (saved.value = false), 2500)
    toast.success('Roles saved')
  } catch (e) {
    toast.error('Could not save roles')
  } finally { saving.value = false }
}
onMounted(load)
</script>
