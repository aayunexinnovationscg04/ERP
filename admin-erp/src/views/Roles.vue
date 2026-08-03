<template>
  <div class="topbar">
    <h1>Role Management</h1>
    <div class="row">
      <span class="muted ico" v-if="saved"><Check :size="16" /> Saved</span>
      <button class="primary ico" @click="save" :disabled="saving"><Check :size="16" /> {{ saving ? 'Saving…' : 'Save changes' }}</button>
    </div>
  </div>
  <p class="muted" style="margin-top:-8px">Global default tabs each role can access. Super Admin is always all-access. Per-user exceptions are set on the user's page.</p>

  <div v-if="loading" class="card" style="padding:16px;margin-top:14px">
    <div class="skel sk-row" v-for="n in 7" :key="n"></div>
  </div>

  <div v-else class="card" style="padding:6px 0;margin-top:14px">
    <table>
      <thead>
        <tr>
          <th>Module / Tab</th>
          <th v-for="r in editableRoles" :key="r" style="text-align:center">{{ r }}</th>
          <th style="text-align:center" class="muted">superadmin</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="g in groups" :key="g">
          <tr><td :colspan="editableRoles.length + 2" class="muted" style="background:var(--panel-2);font-weight:600">{{ g }}</td></tr>
          <tr v-for="m in modulesByGroup[g]" :key="m.key">
            <td>{{ m.label }} <span class="muted" style="font-size:11px">{{ m.key }}</span></td>
            <td v-for="r in editableRoles" :key="r" style="text-align:center">
              <input type="checkbox" v-model="matrix[r][m.key]" />
            </td>
            <td style="text-align:center"><input type="checkbox" checked disabled /></td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Check } from 'lucide-vue-next'
import { getRoles, setRoles } from '../api'
import { toast } from '../toast'

const modules = ref([]); const matrix = ref({})
const loading = ref(true)
const saving = ref(false); const saved = ref(false)
const editableRoles = ['owner', 'manager', 'driver']

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
