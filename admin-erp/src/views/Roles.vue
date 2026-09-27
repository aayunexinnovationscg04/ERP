<template>
  <PageHeader :icon="KeyRound" title="Role Management" description="Default screens each role can open. Admins always have full access. Per-user exceptions are set from the Users page.">
    <span v-if="dirtyCount" class="ph-meta"><CircleDot :size="13" style="color:var(--amber)" /> {{ dirtyCount }} unsaved {{ dirtyCount === 1 ? 'change' : 'changes' }}</span>
    <button v-if="dirtyCount" type="button" class="btn" :disabled="saving" @click="reset"><Undo2 :size="16" /> Discard</button>
    <button type="button" class="btn btn-primary" :disabled="saving || loading || !dirtyCount" @click="save">
      <Save :size="16" /> {{ saving ? 'Saving…' : 'Save changes' }}
    </button>
  </PageHeader>

  <div class="stats">
    <StatCard v-for="r in editableRoles" :key="r" :label="roleLabel(r) + ' screens'" :loading="loading" :icon="roleIcon[r]" :tone="roleTone[r]">
      {{ countFor(r) }}<span class="of"> / {{ modules.length }}</span>
    </StatCard>
    <StatCard label="Admin screens" :loading="loading" :icon="ShieldCheck" tone="navy">
      {{ modules.length }}<span class="of"> / {{ modules.length }}</span>
    </StatCard>
  </div>

  <div class="card">
    <div class="card-head">
      <div><h2>Access matrix</h2><div class="sub">Tick a box to let that role open the screen</div></div>
      <span class="swipe-hint"><ArrowLeftRight :size="13" /> Scroll sideways for all roles</span>
    </div>
    <div v-if="loading" class="card-body"><div class="skel skel-row" v-for="n in 8" :key="n" style="margin-bottom:14px"></div></div>
    <div v-else class="table-wrap">
      <table class="table matrix">
        <thead>
          <tr>
            <th class="sticky-col">Screen</th>
            <th v-for="r in editableRoles" :key="r" class="t-center"><span class="role-badge" :class="r">{{ roleLabel(r) }}</span></th>
            <th class="t-center"><span class="role-badge admin"><Lock :size="11" /> Admin</span></th>
          </tr>
        </thead>
        <tbody>
          <template v-for="g in groups" :key="g">
            <tr class="group-row"><td class="sticky-col">{{ g }} screens</td><td :colspan="editableRoles.length + 1"></td></tr>
            <tr v-for="m in modulesByGroup[g]" :key="m.key">
              <td class="sticky-col">
                <div class="t-primary">{{ m.label }}</div>
                <div class="t-secondary mono">{{ m.key }}</div>
              </td>
              <td v-for="r in editableRoles" :key="r" class="t-center" :class="{ changed: matrix[r][m.key] !== initial[r]?.[m.key] }">
                <MatrixCheckbox v-model="matrix[r][m.key]" :aria-label="`${roleLabel(r)} can open ${m.label}`" />
              </td>
              <td class="t-center"><MatrixCheckbox :model-value="true" disabled :aria-label="`Admin can open ${m.label}`" /></td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import { KeyRound, Save, Undo2, CircleDot, ArrowLeftRight, Lock, ShieldCheck, Store, UserCog, Truck } from 'lucide-vue-next'
import { getRoles, setRoles } from '../api'
import { roleLabel, apiError } from '../format'
import { toast } from '../toast'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import MatrixCheckbox from '../components/MatrixCheckbox.vue'

const modules = ref([]); const matrix = ref({}); const initial = ref({})
const loading = ref(true)
const saving = ref(false)
const editableRoles = ['dealer', 'manager', 'pilot']
const roleIcon = { dealer: Store, manager: UserCog, pilot: Truck }
const roleTone = { dealer: 'brand', manager: 'teal', pilot: 'info' }

const groups = computed(() => [...new Set(modules.value.map((m) => m.group))])
const modulesByGroup = computed(() => {
  const o = {}; modules.value.forEach((m) => { (o[m.group] ||= []).push(m) }); return o
})
const countFor = (r) => modules.value.filter((m) => matrix.value[r]?.[m.key]).length
const dirtyCount = computed(() => {
  let n = 0
  editableRoles.forEach((r) => modules.value.forEach((m) => {
    if (matrix.value[r]?.[m.key] !== initial.value[r]?.[m.key]) n++
  }))
  return n
})
const clone = (o) => JSON.parse(JSON.stringify(o))

async function load() {
  try {
    const d = await getRoles()
    modules.value = d.modules
    const m = {}
    editableRoles.forEach((r) => {
      m[r] = {}; modules.value.forEach((mod) => { m[r][mod.key] = !!d.matrix[r]?.[mod.key] })
    })
    matrix.value = m
    initial.value = clone(m)
  } catch (e) {
    toast.error('Could not load roles')
  } finally { loading.value = false }
}
function reset() { matrix.value = clone(initial.value) }
async function save() {
  saving.value = true
  try {
    await setRoles(matrix.value)
    initial.value = clone(matrix.value)
    toast.success('Role access saved')
  } catch (e) {
    toast.error(apiError(e, 'Could not save roles.'))
  } finally { saving.value = false }
}
onBeforeRouteLeave(() => {
  if (dirtyCount.value && !saving.value) return window.confirm('You have unsaved role changes. Leave without saving?')
})
onMounted(load)
</script>

<style scoped>
.matrix th, .matrix td { padding-top: 10px; padding-bottom: 10px; }
.matrix th.t-center, .matrix td.t-center { width: 120px; min-width: 96px; }
.sticky-col { position: sticky; left: 0; z-index: 1; background: var(--surface); min-width: 180px; }
.matrix thead .sticky-col { background: var(--surface-2); }
.matrix tr.group-row td { background: var(--surface-2); }
.matrix tbody tr:hover .sticky-col { background: var(--surface-2); }
.matrix td.changed { background: var(--amber-soft); }
.swipe-hint { display: none; align-items: center; gap: 6px; font-size: .75rem; font-weight: 600; color: var(--muted); }
@media (max-width: 720px) {
  .swipe-hint { display: inline-flex; }
  .sticky-col { min-width: 132px; max-width: 150px; box-shadow: 1px 0 0 var(--border); }
  .matrix th.t-center, .matrix td.t-center { min-width: 76px; }
  .matrix .role-badge { padding: 0 7px; }
  .matrix th, .matrix td { padding-left: 12px; padding-right: 12px; }
}
</style>
