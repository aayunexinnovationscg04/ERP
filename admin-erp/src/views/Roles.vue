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

  <div v-else>
    <p class="swipe-hint">Swipe sideways to see every role <ArrowLeftRight :size="12" /></p>
    <div class="card" style="padding:6px 0;margin-top:14px">
    <table>
      <thead>
        <tr>
          <th>Module / Tab</th>
          <th v-for="r in editableRoles" :key="r" style="text-align:center" :style="{ color: roleColor(r) }">{{ roleLabel(r) }}</th>
          <th style="text-align:center" :style="{ color: roleColor('admin') }">Admin</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="g in groups" :key="g">
          <tr class="group-row" :style="groupStyle(g)"><td :colspan="editableRoles.length + 2"><span class="grp-dot"></span>{{ g }}</td></tr>
          <motion.tr
            v-for="(m, idx) in modulesByGroup[g]" :key="m.key"
            :initial="{ opacity: 0, y: 4 }" :animate="{ opacity: 1, y: 0 }"
            :transition="{ duration: 0.14, delay: Math.min(idx, 8) * 0.015, ease: [0.4, 0, 0.2, 1] }"
          >
            <td>{{ m.label }} <span class="muted" style="font-size:11px">{{ m.key }}</span></td>
            <td v-for="r in editableRoles" :key="r" style="text-align:center">
              <MatrixCheckbox v-model="matrix[r][m.key]" :color="roleColor(r)" :color-soft="roleColorSoft(r)" />
            </td>
            <td style="text-align:center"><MatrixCheckbox :model-value="true" disabled :color="roleColor('admin')" :color-soft="roleColorSoft('admin')" /></td>
          </motion.tr>
        </template>
      </tbody>
    </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { motion } from 'motion-v'
import { Check, ArrowLeftRight } from 'lucide-vue-next'
import { getRoles, setRoles } from '../api'
import { toast } from '../toast'
import MatrixCheckbox from '../components/MatrixCheckbox.vue'

const modules = ref([]); const matrix = ref({})
const loading = ref(true)
const saving = ref(false); const saved = ref(false)
const editableRoles = ['dealer', 'manager', 'pilot']
const roleLabels = { dealer: 'Dealer', manager: 'Manager', pilot: 'Pilot' }
function roleLabel(r) { return roleLabels[r] || r }

// each role gets its own hue so checked cells show a role-tinted "fingerprint"
// instead of identical black squares everywhere
const roleColors = {
  admin: ['var(--role-admin)', 'var(--role-admin-soft)'],
  dealer: ['var(--role-dealer)', 'var(--role-dealer-soft)'],
  manager: ['var(--role-manager)', 'var(--role-manager-soft)'],
  pilot: ['var(--role-pilot)', 'var(--role-pilot-soft)'],
}
function roleColor(r) { return roleColors[r]?.[0] }
function roleColorSoft(r) { return roleColors[r]?.[1] }

const groups = computed(() => [...new Set(modules.value.map((m) => m.group))])
const modulesByGroup = computed(() => {
  const o = {}; modules.value.forEach((m) => { (o[m.group] ||= []).push(m) }); return o
})
// cycle module groups through a fixed 6-hue accent palette so each group is
// visually distinct at a glance in the matrix — data-driven, not hardcoded names
const groupPalette = ['--grp-1', '--grp-2', '--grp-3', '--grp-4', '--grp-5', '--grp-6']
function groupStyle(g) {
  const idx = groups.value.indexOf(g) % groupPalette.length
  const v = groupPalette[idx]
  return { '--grp-color': `var(${v})`, '--grp-color-soft': `var(${v}-soft)` }
}

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

<style scoped>
/* Only shown on narrow screens where the matrix genuinely needs to scroll
   horizontally (it can't be "stacked" like a simple list - it's a real
   grid comparison). Explicit and unmissable, unlike relying on a subtle
   edge-shadow a phone user might not notice at a glance. */
.swipe-hint {
  display: none; align-items: center; gap: 6px; margin: 10px 2px 0;
  font-size: var(--fs-xs); font-weight: 700; color: var(--brand-bright);
  text-transform: uppercase; letter-spacing: .04em;
}
@media (max-width: 900px) { .swipe-hint { display: inline-flex; } }
</style>
