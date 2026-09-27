<template>
  <PageHeader :icon="Users" title="Users" description="Accounts for every portal. Change roles and companies inline. Use View as to open a dealer's or pilot's portal exactly as they see it (view only).">
    <button type="button" class="btn btn-primary" @click="openCreate"><UserPlus :size="16" /> New user</button>
  </PageHeader>

  <div class="stats">
    <StatCard label="Total users" :value="fmt(users.length)" :icon="Users" tone="navy" :loading="loading" />
    <StatCard label="Active accounts" :value="fmt(activeCount)" :icon="UserCheck" tone="green" :loading="loading" />
    <StatCard label="Disabled" :value="fmt(users.length - activeCount)" :icon="UserX" :tone="users.length - activeCount ? 'amber' : 'navy'" :loading="loading" />
    <StatCard label="Read-only accounts" :value="fmt(readOnlyCount)" :icon="Eye" tone="info" :loading="loading" sub="Non-admins without edit rights" />
  </div>

  <div class="card">
    <div class="toolbar">
      <label class="input-icon">
        <Search :size="16" />
        <input v-model="q" class="input" type="search" placeholder="Search username, email or phone" aria-label="Search users" />
      </label>
      <select v-model="roleFilter" class="select" aria-label="Filter by role">
        <option value="">All roles</option>
        <option v-for="r in roles" :key="r" :value="r">{{ roleLabel(r) }}</option>
      </select>
      <select v-model="companyFilter" class="select" aria-label="Filter by company">
        <option value="">All companies</option>
        <option value="none">No company</option>
        <option v-for="c in companies" :key="c.id" :value="String(c.id)">{{ c.name }}</option>
      </select>
      <button v-if="filtersOn" type="button" class="btn btn-ghost btn-sm" @click="clearFilters"><X :size="14" /> Clear</button>
    </div>
    <div class="table-wrap">
      <table class="table stack users-table">
        <thead>
          <tr><th>User</th><th>Role</th><th>Company</th><th class="t-center">Can edit</th><th class="t-center">Active</th><th class="col-login">Last sign-in</th><th class="t-right">View</th></tr>
        </thead>
        <TableSkeleton v-if="loading" :cols="7" :rows="6" />
        <tbody v-else-if="!filtered.length">
          <tr class="table-empty"><td colspan="7">
            <EmptyState v-if="!users.length" :icon="Users" title="No users yet" text="Create the first account to get started.">
              <button type="button" class="btn btn-primary" @click="openCreate"><UserPlus :size="16" /> New user</button>
            </EmptyState>
            <EmptyState v-else :icon="Search" title="No matching users" text="Try a different search or filter.">
              <button type="button" class="btn" @click="clearFilters">Clear filters</button>
            </EmptyState>
          </td></tr>
        </tbody>
        <tbody v-else>
          <tr v-for="u in pagedRows" :key="u.id" :class="{ 'row-off': !u.is_active }">
            <td class="cell-head">
              <div class="cell-entity">
                <span class="entity-mark round">{{ (u.username || '?')[0] }}</span>
                <div>
                  <div class="t-primary">{{ u.username }} <span v-if="isSelf(u)" class="badge outline" style="height:20px;margin-left:4px">You</span></div>
                  <div class="t-secondary">{{ u.email || u.phone || 'No contact details' }}</div>
                  <div class="t-secondary login-inline">Last sign-in: {{ relTime(u.last_login) }}</div>
                </div>
              </div>
            </td>
            <td data-label="Role">
              <select
                :value="u.role" class="select select-sm role-select" :class="'r-' + u.role" :disabled="isSelf(u) || busyId === u.id"
                :title="isSelf(u) ? 'You cannot change your own role' : 'Change role'" aria-label="Role"
                @change="patch(u, { role: $event.target.value }, 'Role updated')"
              >
                <option v-for="r in roles" :key="r" :value="r">{{ roleLabel(r) }}</option>
              </select>
            </td>
            <td data-label="Company">
              <select
                :value="u.company ?? ''" class="select select-sm" :disabled="busyId === u.id" aria-label="Company"
                @change="patch(u, { company: $event.target.value || null }, 'Company updated')"
              >
                <option value="">No company</option>
                <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </td>
            <td data-label="Can edit" class="t-center">
              <span v-if="u.role === 'admin'" class="muted" title="Admins always have full access">Always</span>
              <ToggleSwitch
                v-else :model-value="u.can_edit" :disabled="busyId === u.id" :aria-label="`Allow ${u.username} to edit`"
                @change="(v) => patch(u, { can_edit: v }, v ? 'Edit rights granted' : 'Account set to read-only')"
              />
            </td>
            <td data-label="Active" class="t-center">
              <ToggleSwitch
                :model-value="u.is_active" :disabled="isSelf(u) || busyId === u.id" :aria-label="`${u.username} active`"
                :title="isSelf(u) ? 'You cannot deactivate your own account' : ''"
                @change="(v) => onActive(u, v)"
              />
            </td>
            <td data-label="Last sign-in" class="nowrap muted col-login" :title="u.last_login ? fmtDateTime(u.last_login) : ''">{{ relTime(u.last_login) }}</td>
            <td data-label="View" class="t-right">
              <button v-if="u.role !== 'admin'" type="button" class="btn btn-sm access-btn" :disabled="!u.is_active || viewingId === u.id"
                      :title="u.is_active ? `Open ${u.username}'s portal in a new tab (view only)` : 'Account is disabled'"
                      :aria-label="`View as ${u.username}`" @click="viewAs(u)">
                <Eye :size="14" /> <span class="access-label">{{ viewingId === u.id ? 'Opening…' : 'View as' }}</span>
              </button>
              <span v-else class="muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>

  <Modal :open="showCreate" title="New user" description="The user signs in to the portal that matches their role." @close="showCreate = false">
    <form id="user-form" class="form-grid" autocomplete="off" @submit.prevent="create">
      <div class="field">
        <label for="nu-username">Username<span class="req">*</span></label>
        <input id="nu-username" v-model="nu.username" class="input" required autocomplete="off" autocapitalize="none" spellcheck="false" />
      </div>
      <div class="field">
        <label for="nu-password">Password<span class="req">*</span></label>
        <input id="nu-password" v-model="nu.password" class="input" type="password" required autocomplete="new-password" />
      </div>
      <div class="field span-2">
        <span class="field-label" id="nu-role-label">Role<span class="req">*</span></span>
        <div class="role-pick" role="radiogroup" aria-labelledby="nu-role-label">
          <button v-for="r in createRoles" :key="r.value" type="button" class="role-opt" :class="{ on: nu.role === r.value }"
                  role="radio" :aria-checked="nu.role === r.value" @click="nu.role = r.value">
            <span class="role-opt-ic"><component :is="r.icon" :size="18" /></span>
            <span class="role-opt-text"><strong>{{ r.label }}</strong><small>{{ r.hint }}</small></span>
          </button>
        </div>
      </div>
      <div class="field span-2">
        <label for="nu-company">Company<span class="req">*</span></label>
        <select id="nu-company" v-model="nu.company" class="select" required>
          <option :value="null" disabled>Select a company</option>
          <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="field">
        <label for="nu-email">Email</label>
        <input id="nu-email" v-model="nu.email" class="input" type="email" autocomplete="off" placeholder="Optional" />
      </div>
      <div class="field">
        <label for="nu-phone">Phone</label>
        <input id="nu-phone" v-model="nu.phone" class="input" type="tel" autocomplete="off" placeholder="Optional" />
      </div>
      <div v-if="msg" class="form-error span-2"><CircleAlert :size="16" /> {{ msg }}</div>
    </form>
    <template #footer>
      <button type="button" class="btn" @click="showCreate = false">Cancel</button>
      <button type="submit" form="user-form" class="btn btn-primary" :disabled="creating || !nu.username || !nu.password">
        {{ creating ? 'Creating…' : 'Create user' }}
      </button>
    </template>
  </Modal>

  <ConfirmDialog
    :open="!!deactivating" :title="`Deactivate ${deactivating?.username}?`" confirm-label="Deactivate"
    :busy="busyId === deactivating?.id" @cancel="deactivating = null" @confirm="confirmDeactivate"
  >
    They will be signed out and won't be able to sign in until the account is reactivated.
  </ConfirmDialog>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Users, UserPlus, UserCheck, UserX, Eye, Search, X, CircleAlert, Truck, Navigation } from 'lucide-vue-next'
import { getUsers, createUser, updateUser, getCompanies, viewAsTicket } from '../api'
import { auth } from '../auth'
import { fmt, fmtDateTime, relTime, roleLabel, apiError } from '../format'
import { toast } from '../toast'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import TableSkeleton from '../components/TableSkeleton.vue'
import Modal from '../components/Modal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'
import ToggleSwitch from '../components/ToggleSwitch.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const route = useRoute()
const roles = ['dealer', 'manager', 'pilot', 'admin']
const users = ref([]); const companies = ref([])
const loading = ref(true)
const busyId = ref(null)

const q = ref('')
const roleFilter = ref('')
const companyFilter = ref(route.query.company ? String(route.query.company) : '')
watch(() => route.query.company, (c) => { companyFilter.value = c ? String(c) : '' })
const filtersOn = computed(() => q.value || roleFilter.value || companyFilter.value)
function clearFilters() { q.value = ''; roleFilter.value = ''; companyFilter.value = '' }

const activeCount = computed(() => users.value.filter((u) => u.is_active).length)
const readOnlyCount = computed(() => users.value.filter((u) => u.role !== 'admin' && !u.can_edit).length)
const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  return users.value.filter((u) => {
    if (roleFilter.value && u.role !== roleFilter.value) return false
    if (companyFilter.value === 'none' && u.company) return false
    if (companyFilter.value && companyFilter.value !== 'none' && String(u.company) !== companyFilter.value) return false
    if (term && ![u.username, u.email, u.phone].some((f) => (f || '').toLowerCase().includes(term))) return false
    return true
  })
})
const isSelf = (u) => auth.user && String(auth.user.id) === String(u.id)

async function load() {
  try {
    ;[users.value, companies.value] = await Promise.all([getUsers(), getCompanies()])
  } catch (e) {
    toast.error('Could not load users')
  } finally { loading.value = false }
}

// ---- create ----
const showCreate = ref(false); const msg = ref(''); const creating = ref(false)
const blank = () => ({ username: '', password: '', role: 'dealer', company: null, email: '', phone: '' })
const nu = ref(blank())
function openCreate() { nu.value = blank(); msg.value = ''; showCreate.value = true }
// New accounts are dealers or pilots only, and always belong to a company.
const createRoles = [
  { value: 'dealer', label: 'Dealer', hint: 'Dealer portal', icon: Truck },
  { value: 'pilot', label: 'Pilot', hint: 'Pilot app', icon: Navigation },
]
async function create() {
  msg.value = ''
  if (!nu.value.company) { msg.value = 'Choose the company this user belongs to.'; return }
  creating.value = true
  try {
    await createUser({ ...nu.value, username: nu.value.username.trim() })
    showCreate.value = false
    toast.success(`User ${nu.value.username} created`)
    await load()
  } catch (e) {
    msg.value = apiError(e, 'Could not create the user.')
  } finally { creating.value = false }
}

// ---- view as: open the user's own portal in a new tab, read-only ----
const viewingId = ref(null)
function portalOrigin(portal) {
  const { protocol, hostname } = location
  if (hostname.startsWith('admin.')) return `${protocol}//${portal}.${hostname.slice(6)}`
  return `${protocol}//${hostname}:${{ dealer: 5173, pilot: 5174 }[portal]}`   // local dev servers
}
async function viewAs(u) {
  // Open the tab synchronously (inside the click) so pop-up blockers allow it.
  const tab = window.open('about:blank', '_blank')
  viewingId.value = u.id
  try {
    const { ticket, portal } = await viewAsTicket(u.id)
    const url = `${portalOrigin(portal)}/view-as#t=${encodeURIComponent(ticket)}`
    if (!tab) { toast.error('Allow pop-ups for this site to open the view.'); return }
    tab.opener = null
    tab.location.replace(url)
  } catch (e) {
    tab?.close()
    toast.error(apiError(e, 'Could not open the view.'))
  } finally {
    viewingId.value = null
  }
}

// ---- inline edits ----
async function patch(u, body, okMsg = 'User updated') {
  busyId.value = u.id
  try {
    await updateUser(u.id, body)
    toast.success(okMsg)
  } catch (e) {
    toast.error(apiError(e, 'Could not update the user.'))
  } finally {
    await load()
    busyId.value = null
  }
}
const deactivating = ref(null)
function onActive(u, v) {
  if (v) patch(u, { is_active: true }, `${u.username} reactivated`)
  else deactivating.value = u
}
async function confirmDeactivate() {
  const u = deactivating.value
  await patch(u, { is_active: false }, `${u.username} deactivated`)
  deactivating.value = null
}
onMounted(load)

// pagination (resets to page 1 when search/filters change)
const pager = usePaging(filtered)
const pagedRows = pager.rows
</script>

<style scoped>
/* new-user role picker: two large options, easy to tap on phones */
.role-pick { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.role-opt {
  display: flex; align-items: center; gap: 10px; min-height: 56px; padding: 10px 12px; text-align: left;
  border: 1px solid var(--border-strong); border-radius: 10px; background: var(--surface); color: var(--text);
  font: inherit; cursor: pointer; box-shadow: none; transform: none;
}
.role-opt:hover { border-color: var(--muted-2); transform: none; }
.role-opt:focus-visible { outline: none; box-shadow: 0 0 0 3px var(--brand-ring); }
.role-opt.on { border-color: var(--brand); background: var(--brand-soft); }
.role-opt-ic { flex: none; width: 34px; height: 34px; border-radius: 8px; display: grid; place-items: center; background: var(--surface-3); color: var(--muted); }
.role-opt.on .role-opt-ic { background: var(--brand); color: #FFFFFF; }
.role-opt-text { display: flex; flex-direction: column; line-height: 1.25; }
.role-opt-text strong { font-size: .9rem; }
.role-opt-text small { font-size: .75rem; color: var(--muted); }
.role-select { font-weight: 700; width: auto; min-width: 118px; border-color: transparent; }
.role-select.r-admin { background-color: var(--role-admin-soft); color: var(--role-admin); }
.role-select.r-dealer { background-color: var(--role-dealer-soft); color: var(--role-dealer); }
.role-select.r-manager { background-color: var(--role-manager-soft); color: var(--role-manager); }
.role-select.r-pilot { background-color: var(--role-pilot-soft); color: var(--role-pilot); }
.role-select:disabled { opacity: 1; cursor: default; background-image: none; padding-right: 10px; }
.users-table td .select-sm:not(.role-select) { width: auto; min-width: 150px; max-width: 200px; }
.login-inline { display: none; }
@media (max-width: 1180px) and (min-width: 721px) {
  .users-table .col-login { display: none; }
  .login-inline { display: block; }
  .users-table td .select-sm:not(.role-select) { min-width: 0; max-width: 150px; }
  .role-select { min-width: 104px; }
}
@media (max-width: 1320px) and (min-width: 721px) {
  .users-table .access-label { display: none; }
  .users-table .access-btn { width: 36px; padding: 0; }
  .users-table th, .users-table td { padding-left: 12px; padding-right: 12px; }
}
.row-off .t-primary { color: var(--muted); }
@media (max-width: 720px) {
  .users-table td .select-sm:not(.role-select), .users-table td .role-select { min-width: 0; width: 100%; max-width: 100%; }
  .users-table .access-btn { width: 100%; justify-content: center; min-height: 40px; }
}
</style>
