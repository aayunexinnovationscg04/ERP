<template>
  <PageHeader :icon="Building2" title="Companies" description="Fleet operators registered on Fuel Guard X, their status and user accounts.">
    <button type="button" class="btn btn-primary" @click="openCreate"><Plus :size="16" /> Add company</button>
  </PageHeader>

  <div class="stats">
    <StatCard label="Total companies" :value="fmt(companies.length)" :icon="Building2" tone="navy" :loading="loading" />
    <StatCard label="Active" :value="fmt(activeCount)" :icon="CircleCheck" tone="green" :loading="loading" />
    <StatCard label="Suspended" :value="fmt(companies.length - activeCount)" :icon="Ban" :tone="companies.length - activeCount ? 'red' : 'navy'" :loading="loading" />
    <StatCard label="Users in companies" :value="fmt(companyUserTotal)" :icon="Users" tone="info" :loading="loading" />
  </div>

  <div class="card">
    <div class="toolbar">
      <label class="input-icon">
        <Search :size="16" />
        <input v-model="q" class="input" type="search" placeholder="Search by name or slug" aria-label="Search companies" />
      </label>
      <div class="seg" role="group" aria-label="Filter by status">
        <button v-for="f in filters" :key="f.key" type="button" :class="{ on: status === f.key }" @click="status = f.key">
          {{ f.label }} <span class="count">{{ f.count }}</span>
        </button>
      </div>
    </div>
    <div class="table-wrap">
      <table class="table stack">
        <thead>
          <tr><th>Company</th><th>Status</th><th class="t-right">Users</th><th>Registered</th><th class="t-right">Actions</th></tr>
        </thead>
        <TableSkeleton v-if="loading" :cols="5" />
        <tbody v-else-if="!filtered.length">
          <tr class="table-empty"><td colspan="5">
            <EmptyState v-if="!companies.length" :icon="Building2" title="No companies yet" text="Add the first fleet operator to start onboarding their users and vehicles.">
              <button type="button" class="btn btn-primary" @click="openCreate"><Plus :size="16" /> Add company</button>
            </EmptyState>
            <EmptyState v-else :icon="Search" title="No matching companies" text="Try a different search or status filter." />
          </td></tr>
        </tbody>
        <tbody v-else>
          <tr v-for="c in filtered" :key="c.id">
            <td class="cell-head">
              <div class="cell-entity">
                <span class="entity-mark">{{ initials(c.name) }}</span>
                <div><div class="t-primary">{{ c.name }}</div><div class="t-secondary mono">{{ c.slug }}</div></div>
              </div>
            </td>
            <td data-label="Status">
              <span class="badge" :class="c.status === 'active' ? 'success' : 'danger'"><span class="bdot"></span>{{ c.status === 'active' ? 'Active' : 'Suspended' }}</span>
            </td>
            <td data-label="Users" class="t-right num">
              <router-link :to="{ path: '/users', query: { company: c.id } }" class="num" title="View this company's users">{{ usersByCompany[c.id] || 0 }}</router-link>
            </td>
            <td data-label="Registered" class="nowrap muted">{{ fmtDate(c.created_at) }}</td>
            <td data-label="Actions" class="t-right">
              <button v-if="c.status === 'active'" type="button" class="btn btn-sm btn-danger-ghost" @click="askToggle(c)"><Ban :size="14" /> Suspend</button>
              <button v-else type="button" class="btn btn-sm btn-success-ghost" @click="askToggle(c)"><RotateCcw :size="14" /> Reactivate</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!loading && companies.length" class="card-foot">
      <span>Showing {{ filtered.length }} of {{ companies.length }} {{ companies.length === 1 ? 'company' : 'companies' }}</span>
    </div>
  </div>

  <Modal :open="showCreate" title="Add company" description="Creates a new tenant. Add its users from the Users page afterwards." @close="showCreate = false">
    <form id="company-form" class="form-grid" @submit.prevent="create">
      <div class="field span-2">
        <label for="co-name">Company name<span class="req">*</span></label>
        <input id="co-name" v-model="form.name" class="input" required maxlength="200" placeholder="e.g. Shree Logistics" autocomplete="off" @input="syncSlug" />
      </div>
      <div class="field span-2">
        <label for="co-slug">Slug<span class="req">*</span></label>
        <input id="co-slug" v-model="form.slug" class="input mono" required maxlength="80" pattern="[a-zA-Z0-9_\-]+" placeholder="shree-logistics" autocomplete="off" @input="slugTouched = true" />
        <span class="help">Unique short ID. Letters, numbers, hyphens and underscores only.</span>
      </div>
      <div v-if="formError" class="form-error span-2"><CircleAlert :size="16" /> {{ formError }}</div>
    </form>
    <template #footer>
      <button type="button" class="btn" @click="showCreate = false">Cancel</button>
      <button type="submit" form="company-form" class="btn btn-primary" :disabled="saving || !form.name || !form.slug">
        {{ saving ? 'Creating…' : 'Create company' }}
      </button>
    </template>
  </Modal>

  <ConfirmDialog
    :open="!!pending" :busy="toggling"
    :title="pending?.status === 'active' ? `Suspend ${pending?.name}?` : `Reactivate ${pending?.name}?`"
    :tone="pending?.status === 'active' ? 'danger' : 'ok'"
    :confirm-label="pending?.status === 'active' ? 'Suspend company' : 'Reactivate company'"
    @cancel="pending = null" @confirm="toggleStatus"
  >
    <template v-if="pending?.status === 'active'">
      The company becomes read-only: its {{ usersByCompany[pending?.id] || 0 }} user account(s) can still sign in and view data but can't change anything. No data is deleted, and you can reactivate it at any time.
    </template>
    <template v-else>The company will be marked as active again.</template>
  </ConfirmDialog>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { Building2, CircleCheck, Ban, Users, Search, Plus, RotateCcw, CircleAlert } from 'lucide-vue-next'
import { getCompanies, getUsers, createCompany, updateCompany } from '../api'
import { fmt, fmtDate, apiError } from '../format'
import { toast } from '../toast'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import TableSkeleton from '../components/TableSkeleton.vue'
import Modal from '../components/Modal.vue'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const companies = ref([])
const users = ref([])
const loading = ref(true)
const q = ref('')
const status = ref('all')

const activeCount = computed(() => companies.value.filter((c) => c.status === 'active').length)
const usersByCompany = computed(() => {
  const m = {}
  users.value.forEach((u) => { if (u.company) m[u.company] = (m[u.company] || 0) + 1 })
  return m
})
const companyUserTotal = computed(() => users.value.filter((u) => u.company).length)
const filters = computed(() => [
  { key: 'all', label: 'All', count: companies.value.length },
  { key: 'active', label: 'Active', count: activeCount.value },
  { key: 'suspended', label: 'Suspended', count: companies.value.length - activeCount.value },
])
const filtered = computed(() => {
  const term = q.value.trim().toLowerCase()
  return companies.value.filter((c) =>
    (status.value === 'all' || (status.value === 'active' ? c.status === 'active' : c.status !== 'active'))
    && (!term || c.name.toLowerCase().includes(term) || c.slug.toLowerCase().includes(term)))
})

function initials(name) {
  return (name || '?').split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join('')
}

async function load() {
  try {
    ;[companies.value, users.value] = await Promise.all([getCompanies(), getUsers()])
  } catch (e) {
    toast.error('Could not load companies')
  } finally { loading.value = false }
}
onMounted(load)

// ---- create ----
const showCreate = ref(false)
const saving = ref(false)
const formError = ref('')
const form = ref({ name: '', slug: '' })
const slugTouched = ref(false)
const slugify = (s) => s.toLowerCase().normalize('NFKD').replace(/[^\w\s-]/g, '').trim().replace(/[\s_]+/g, '-').replace(/-+/g, '-').slice(0, 80)
function syncSlug() { if (!slugTouched.value) form.value.slug = slugify(form.value.name) }
function openCreate() {
  form.value = { name: '', slug: '' }; slugTouched.value = false; formError.value = ''; showCreate.value = true
}
async function create() {
  saving.value = true; formError.value = ''
  try {
    const c = await createCompany({ name: form.value.name.trim(), slug: form.value.slug.trim() })
    showCreate.value = false
    toast.success(`${c.name} added`)
    await load()
  } catch (e) {
    formError.value = apiError(e, 'Could not create the company.')
  } finally { saving.value = false }
}

// ---- suspend / reactivate ----
const pending = ref(null)
const toggling = ref(false)
function askToggle(c) { pending.value = c }
async function toggleStatus() {
  const c = pending.value
  const next = c.status === 'active' ? 'suspended' : 'active'
  toggling.value = true
  try {
    await updateCompany(c.id, { status: next })
    toast.success(next === 'active' ? `${c.name} reactivated` : `${c.name} suspended`)
    pending.value = null
    await load()
  } catch (e) {
    toast.error(apiError(e, 'Could not update the company.'))
  } finally { toggling.value = false }
}
</script>
