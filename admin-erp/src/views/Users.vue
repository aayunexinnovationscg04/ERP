<template>
  <PageHeader>
    <button type="button" class="btn btn-primary" @click="openCreate"><UserPlus :size="16" /> New {{ kindLabel.toLowerCase() }}</button>
  </PageHeader>

  <div class="stats">
    <StatCard :label="kindLabel + 's'" :value="fmt(people.length)" :icon="kindIcon" tone="navy" :loading="loading" />
    <StatCard label="Active" :value="fmt(activeCount)" :icon="UserCheck" tone="green" :loading="loading" />
    <StatCard label="Disabled" :value="fmt(people.length - activeCount)" :icon="UserX" :tone="people.length - activeCount ? 'amber' : 'navy'" :loading="loading" />
    <StatCard label="View only (can't edit)" :value="fmt(readOnlyCount)" :icon="Eye" tone="info" :loading="loading" />
  </div>

  <div class="card">
    <div class="toolbar">
      <label class="input-icon">
        <Search :size="16" />
        <input v-model="q" class="input" type="search" placeholder="Search username, email or phone" aria-label="Search users" />
      </label>
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
          <tr><th>{{ kindLabel }}</th><th v-if="isDealers">Role</th><th>Company</th><th class="t-center">Can edit</th><th class="t-center">Active</th><th class="col-login">Last sign-in</th><th class="t-right">Actions</th></tr>
        </thead>
        <TableSkeleton v-if="loading" :cols="cols" :rows="6" />
        <tbody v-else-if="!filtered.length">
          <tr class="table-empty"><td :colspan="cols">
            <EmptyState v-if="!people.length" :icon="kindIcon" :title="`No ${kindLabel.toLowerCase()}s yet`" text="Create the first account to get started.">
              <button type="button" class="btn btn-primary" @click="openCreate"><UserPlus :size="16" /> New {{ kindLabel.toLowerCase() }}</button>
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
            <td v-if="isDealers" data-label="Role"><span class="role-badge" :class="'r-' + u.role">{{ roleLabel(u.role) }}</span></td>
            <td data-label="Company">
              <select
                :value="u.company ?? ''" class="select select-sm" :disabled="busyId === u.id" aria-label="Company"
                @change="patch(u, { company: $event.target.value || null }, 'Company updated')"
              >
                <option value="" disabled>Select a company</option>
                <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </td>
            <td data-label="Can edit" class="t-center">
              <ToggleSwitch
                :model-value="u.can_edit" :disabled="busyId === u.id" :aria-label="`Allow ${u.username} to edit`"
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
            <td data-label="Actions" class="t-right">
              <div class="row-actions">
                <button type="button" class="btn btn-sm access-btn" :disabled="!u.is_active || viewingId === u.id"
                        :title="u.is_active ? `Open ${u.username}'s portal in a new tab (view only)` : 'Account is disabled'"
                        :aria-label="`View as ${u.username}`" @click="viewAs(u)">
                  <Eye :size="14" /> <span class="access-label">{{ viewingId === u.id ? 'Opening…' : 'View as' }}</span>
                </button>
                <button type="button" class="btn btn-sm access-btn" :title="`Set a new password for ${u.username}`"
                        :aria-label="`Reset password for ${u.username}`" @click="openReset(u)">
                  <KeyRound :size="14" /> <span class="access-label">Password</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </div>

  <Modal :open="showCreate" :title="`New ${kindLabel.toLowerCase()}`" :description="isDealers ? 'Signs in to the Dealer portal.' : 'Signs in to the Pilot app.'" @close="showCreate = false">
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
        <label for="nu-company">Company<span class="req">*</span></label>
        <select id="nu-company" v-model="nu.company" class="select" required>
          <option :value="null" disabled>Select a company</option>
          <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
      <div class="field">
        <label for="nu-phone">Phone<span class="req">*</span></label>
        <input id="nu-phone" v-model="nu.phone" class="input" type="tel" inputmode="tel" autocomplete="off" required placeholder="10-digit mobile number" />
      </div>
      <div class="field">
        <label for="nu-email">Email</label>
        <input id="nu-email" v-model="nu.email" class="input" type="email" autocomplete="off" placeholder="Optional" />
      </div>
      <div v-if="msg" class="form-error span-2"><CircleAlert :size="16" /> {{ msg }}</div>
    </form>
    <template #footer>
      <button type="button" class="btn" @click="showCreate = false">Cancel</button>
      <button type="submit" form="user-form" class="btn btn-primary" :disabled="creating || !nu.username || !nu.password || !nu.phone">
        {{ creating ? 'Creating…' : `Create ${kindLabel.toLowerCase()}` }}
      </button>
    </template>
  </Modal>

  <Modal :open="!!resetting" :title="`New password for ${resetting?.username}`" description="They'll be signed out everywhere and must use the new password." size="sm" @close="resetting = null">
    <form id="reset-form" class="form-grid" autocomplete="off" @submit.prevent="savePassword">
      <div class="field span-2">
        <label for="rp-password">New password<span class="req">*</span></label>
        <div class="pw-row">
          <input id="rp-password" v-model="newPassword" class="input" :type="showNewPw ? 'text' : 'password'" autocomplete="new-password" required minlength="8" />
          <button type="button" class="btn" :aria-label="showNewPw ? 'Hide password' : 'Show password'" @click="showNewPw = !showNewPw">
            <component :is="showNewPw ? EyeOff : Eye" :size="16" />
          </button>
          <button type="button" class="btn" title="Generate a strong password" aria-label="Generate a strong password" @click="generatePassword"><Wand2 :size="16" /></button>
        </div>
        <span class="help">At least 8 characters.</span>
      </div>
      <div v-if="resetMsg" class="form-error span-2"><CircleAlert :size="16" /> {{ resetMsg }}</div>
    </form>
    <template #footer>
      <button type="button" class="btn" @click="resetting = null">Cancel</button>
      <button type="submit" form="reset-form" class="btn btn-primary" :disabled="savingPw || newPassword.length < 8">
        {{ savingPw ? 'Saving…' : 'Set password' }}
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
import { Users, UserPlus, UserCheck, UserX, Eye, EyeOff, KeyRound, Wand2, Search, X, CircleAlert, Truck, Navigation } from 'lucide-vue-next'
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

// One page, two sections: /dealers (dealers + managers) and /pilots.
const props = defineProps({ kind: { type: String, default: 'dealer' } })
const isDealers = computed(() => props.kind !== 'pilot')
const kindLabel = computed(() => (isDealers.value ? 'Dealer' : 'Pilot'))
const kindIcon = computed(() => (isDealers.value ? Truck : Navigation))
const kindRoles = computed(() => (isDealers.value ? ['dealer', 'manager'] : ['pilot']))
const cols = computed(() => (isDealers.value ? 7 : 6))

const route = useRoute()
const users = ref([]); const companies = ref([])
const loading = ref(true)
const busyId = ref(null)

const q = ref('')
const companyFilter = ref(route.query.company ? String(route.query.company) : '')
watch(() => route.query.company, (c) => { companyFilter.value = c ? String(c) : '' })
const filtersOn = computed(() => q.value || companyFilter.value)
function clearFilters() { q.value = ''; companyFilter.value = '' }
watch(() => props.kind, () => { q.value = '' })

const people = computed(() => users.value.filter((u) => kindRoles.value.includes(u.role)))
const activeCount = computed(() => people.value.filter((u) => u.is_active).length)
const readOnlyCount = computed(() => people.value.filter((u) => !u.can_edit).length)
const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  return people.value.filter((u) => {
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
// The section decides the role (Dealers -> dealer, Pilots -> pilot); company and phone are required.
const blank = () => ({ username: '', password: '', role: isDealers.value ? 'dealer' : 'pilot', company: null, email: '', phone: '' })
const nu = ref(blank())
function openCreate() { nu.value = blank(); msg.value = ''; showCreate.value = true }
async function create() {
  msg.value = ''
  if (!nu.value.company) { msg.value = 'Choose the company this account belongs to.'; return }
  if (!/^\+?[0-9][0-9 -]{8,18}[0-9]$/.test(nu.value.phone.trim())) { msg.value = 'Enter a valid phone number (10–15 digits).'; return }
  creating.value = true
  try {
    await createUser({ ...nu.value, username: nu.value.username.trim() })
    showCreate.value = false
    toast.success(`${kindLabel.value} ${nu.value.username} created`)
    await load()
  } catch (e) {
    msg.value = apiError(e, 'Could not create the user.')
  } finally { creating.value = false }
}

// ---- password reset: the admin sets a new one, no old password needed ----
const resetting = ref(null); const newPassword = ref(''); const showNewPw = ref(false)
const savingPw = ref(false); const resetMsg = ref('')
function openReset(u) { resetting.value = u; newPassword.value = ''; showNewPw.value = false; resetMsg.value = '' }
function generatePassword() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789'
  const bytes = crypto.getRandomValues(new Uint8Array(12))
  newPassword.value = Array.from(bytes, (b) => chars[b % chars.length]).join('')
  showNewPw.value = true
}
async function savePassword() {
  resetMsg.value = ''; savingPw.value = true
  try {
    await updateUser(resetting.value.id, { password: newPassword.value })
    toast.success(`Password updated for ${resetting.value.username}`)
    resetting.value = null
  } catch (e) {
    resetMsg.value = apiError(e, 'Could not update the password.')
  } finally { savingPw.value = false }
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
/* read-only role badge (roles can't be changed) */
.role-badge { display: inline-flex; align-items: center; height: 26px; padding: 0 10px; border-radius: 999px; font-size: .78rem; font-weight: 700; }
.role-badge.r-dealer { background: var(--role-dealer-soft); color: var(--role-dealer); }
.role-badge.r-manager { background: var(--role-manager-soft); color: var(--role-manager); }
.role-badge.r-pilot { background: var(--role-pilot-soft); color: var(--role-pilot); }
.row-actions { display: inline-flex; gap: 6px; justify-content: flex-end; flex-wrap: nowrap; }
.pw-row { display: flex; gap: 6px; }
.pw-row .input { flex: 1; min-width: 0; }
.pw-row .btn { flex: none; width: 44px; padding: 0; justify-content: center; }
.users-table td .select-sm { width: auto; min-width: 150px; max-width: 200px; }
.login-inline { display: none; }
@media (max-width: 1180px) and (min-width: 721px) {
  .users-table .col-login { display: none; }
  .login-inline { display: block; }
  .users-table td .select-sm { min-width: 0; max-width: 150px; }
}
@media (max-width: 1480px) and (min-width: 721px) {
  .users-table .access-label { display: none; }
  .users-table .access-btn { width: 36px; padding: 0; }
  .users-table th, .users-table td { padding-left: 12px; padding-right: 12px; }
}
.row-off .t-primary { color: var(--muted); }
@media (max-width: 720px) {
  .users-table td .select-sm { min-width: 0; width: 100%; max-width: 100%; }
  .row-actions { display: grid; grid-template-columns: 1fr 1fr; width: 100%; }
  .users-table .access-btn { width: 100%; justify-content: center; min-height: 40px; }
}
</style>
