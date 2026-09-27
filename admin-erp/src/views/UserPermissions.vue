<template>
  <router-link to="/users" class="back-link"><ArrowLeft :size="15" /> All users</router-link>
  <PageHeader :icon="SlidersHorizontal" :title="user ? `Screen access · ${user.username}` : 'Screen access'">
    <template #description>
      Each screen follows the <b>{{ roleLabel(data.role) }}</b> role default unless you grant or deny it for this person.
      Role defaults are edited in <router-link to="/roles">Role Management</router-link>.
    </template>
    <span v-if="dirtyCount" class="ph-meta"><CircleDot :size="13" style="color:var(--amber)" /> {{ dirtyCount }} unsaved {{ dirtyCount === 1 ? 'change' : 'changes' }}</span>
    <button v-if="dirtyCount" type="button" class="btn" :disabled="saving" @click="reset"><Undo2 :size="16" /> Discard</button>
    <button type="button" class="btn btn-primary" :disabled="saving || loading || !dirtyCount" @click="save">
      <Save :size="16" /> {{ saving ? 'Saving…' : 'Save changes' }}
    </button>
  </PageHeader>

  <div v-if="!loading && user" class="card user-strip">
    <span class="entity-mark round">{{ user.username[0] }}</span>
    <div class="us-main">
      <div class="t-primary">{{ user.username }}</div>
      <div class="t-secondary">{{ user.company_name || 'No company' }}</div>
    </div>
    <span class="role-badge" :class="data.role">{{ roleLabel(data.role) }}</span>
    <span class="badge" :class="user.is_active ? 'success' : 'neutral'"><span class="bdot"></span>{{ user.is_active ? 'Active' : 'Disabled' }}</span>
    <span class="us-count"><b>{{ effectiveCount }}</b> of {{ modules.length }} screens allowed</span>
  </div>

  <div v-if="data.role === 'admin' && !loading" class="notice info"><Info :size="16" /> <span>Admins can open every screen. Overrides have no effect on admin accounts.</span></div>

  <div class="card">
    <div class="table-wrap">
      <table class="table stack perm-table">
        <thead><tr><th>Screen</th><th>Role default</th><th>This user</th><th>Result</th></tr></thead>
        <TableSkeleton v-if="loading" :cols="4" :rows="7" />
        <tbody v-else-if="!modules.length">
          <tr class="table-empty"><td colspan="4"><EmptyState title="No screens defined" /></td></tr>
        </tbody>
        <tbody v-else>
          <template v-for="g in groups" :key="g">
            <tr class="group-row"><td colspan="4">{{ g }} screens</td></tr>
            <tr v-for="m in byGroup[g]" :key="m.key" :class="{ changed: state[m.key] !== initial[m.key] }">
              <td class="cell-head">
                <div class="t-primary">{{ m.label }}</div>
                <div class="t-secondary mono">{{ m.key }}</div>
              </td>
              <td data-label="Role default">
                <span class="badge" :class="data.role_defaults[m.key] ? 'success' : 'neutral'">
                  <component :is="data.role_defaults[m.key] ? Check : Minus" :size="13" />
                  {{ data.role_defaults[m.key] ? 'Allowed' : 'Not allowed' }}
                </span>
              </td>
              <td data-label="This user">
                <div class="seg" role="radiogroup" :aria-label="`Access to ${m.label}`">
                  <button
                    v-for="o in options" :key="o.value" type="button" role="radio"
                    :aria-checked="state[m.key] === o.value" :class="{ on: state[m.key] === o.value, [o.value]: true }"
                    @click="state[m.key] = o.value"
                  >{{ o.label }}</button>
                </div>
              </td>
              <td data-label="Result">
                <span class="status-dot" :class="effective(m.key) ? 'green' : ''">{{ effective(m.key) ? 'Can open' : 'Hidden' }}</span>
              </td>
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
import { ArrowLeft, SlidersHorizontal, Check, Minus, Save, Undo2, CircleDot, Info } from 'lucide-vue-next'
import { getUserPerms, setUserPerms, getModules, getUsers } from '../api'
import { roleLabel, apiError } from '../format'
import { toast } from '../toast'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'
import TableSkeleton from '../components/TableSkeleton.vue'

const props = defineProps({ id: [String, Number] })
const modules = ref([])
const user = ref(null)
const data = ref({ role: '', role_defaults: {}, overrides: {}, effective: [] })
const state = ref({})   // module -> 'default' | 'allow' | 'deny'
const initial = ref({})
const loading = ref(true)
const saving = ref(false)
const options = [
  { value: 'default', label: 'Default' },
  { value: 'allow', label: 'Grant' },
  { value: 'deny', label: 'Deny' },
]

const groups = computed(() => [...new Set(modules.value.map((m) => m.group))])
const byGroup = computed(() => {
  const o = {}; modules.value.forEach((m) => { (o[m.group] ||= []).push(m) }); return o
})
const dirtyCount = computed(() => modules.value.filter((m) => state.value[m.key] !== initial.value[m.key]).length)
const effectiveCount = computed(() => modules.value.filter((m) => effective(m.key)).length)

function effective(key) {
  if (data.value.role === 'admin') return true
  const s = state.value[key]
  if (s === 'allow') return true
  if (s === 'deny') return false
  return !!data.value.role_defaults[key]
}

async function load() {
  try {
    const [mods, perms, users] = await Promise.all([getModules(), getUserPerms(props.id), getUsers().catch(() => [])])
    modules.value = mods; data.value = perms
    user.value = users.find((u) => String(u.id) === String(props.id)) || null
    const st = {}
    mods.forEach((m) => {
      const ov = perms.overrides[m.key]
      st[m.key] = ov === undefined ? 'default' : (ov ? 'allow' : 'deny')
    })
    state.value = st
    initial.value = { ...st }
  } catch (e) {
    toast.error(apiError(e, 'Could not load this user\'s access.'))
  } finally { loading.value = false }
}
function reset() { state.value = { ...initial.value } }
async function save() {
  saving.value = true
  const overrides = {}
  modules.value.forEach((m) => {
    const s = state.value[m.key]
    overrides[m.key] = s === 'default' ? null : s === 'allow'
  })
  try {
    await setUserPerms(props.id, overrides); await load()
    toast.success('Screen access saved')
  } catch (e) {
    toast.error(apiError(e, 'Could not save screen access.'))
  } finally { saving.value = false }
}
onBeforeRouteLeave(() => {
  if (dirtyCount.value && !saving.value) return window.confirm('You have unsaved access changes. Leave without saving?')
})
onMounted(load)
</script>

<style scoped>
.user-strip { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding: 14px 18px; margin-bottom: 16px; }
.us-main { flex: 1 1 160px; min-width: 0; }
.us-count { font-size: .8125rem; color: var(--muted); }
.us-count b { color: var(--ink-strong); }
.perm-table .seg button.on.allow { background: var(--green-soft); color: var(--green); box-shadow: none; }
.perm-table .seg button.on.deny { background: var(--red-soft); color: var(--red); box-shadow: none; }
.perm-table tr.changed td:first-child { box-shadow: inset 3px 0 0 var(--amber); }
@media (max-width: 720px) {
  .perm-table tr.changed td:first-child { box-shadow: none; }
  .perm-table tr.changed { box-shadow: inset 3px 0 0 var(--amber); }
}
</style>
