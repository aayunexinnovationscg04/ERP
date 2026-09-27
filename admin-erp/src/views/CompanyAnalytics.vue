<template>
  <PageHeader :icon="ChartColumn" title="Company Analytics" description="User accounts and sign-in activity for each company, from live platform records." />

  <div class="stats">
    <StatCard label="Companies" :value="fmt(companies.length)" :icon="Building2" tone="navy" :loading="loading" />
    <StatCard label="Company users" :value="fmt(totals.users)" :icon="Users" tone="info" :loading="loading" :sub="loading ? '' : `${fmt(totals.active)} active accounts`" />
    <StatCard label="Signed in, last 30 days" :value="fmt(totals.recent)" :icon="LogIn" tone="green" :loading="loading" :sub="loading ? '' : pctText(totals.recent, totals.users) + ' of company users'" />
    <StatCard label="Never signed in" :value="fmt(totals.never)" :icon="UserX" :tone="totals.never ? 'amber' : 'navy'" :loading="loading" />
  </div>

  <div class="grid-2">
    <section class="card">
      <div class="card-head">
        <div><h2>Users by company</h2><div class="sub">Accounts per company, split by role</div></div>
      </div>
      <div class="card-body">
        <div v-if="loading" class="bars"><div v-for="n in 4" :key="n" class="skel skel-row"></div></div>
        <EmptyState v-else-if="!rows.length" :icon="Building2" title="No companies yet" />
        <template v-else>
          <div class="bars">
            <div v-for="d in rows" :key="d.id" class="bar-row" :title="`${d.name}: ${d.dealer} dealer, ${d.manager} manager, ${d.pilot} pilot`">
              <span class="bar-label">{{ d.name }}</span>
              <div class="bar-track">
                <div :style="{ display: 'flex', gap: '2px', height: '100%', width: (d.users / maxUsers * 100) + '%' }">
                  <span v-for="r in roleKeys" v-show="d[r]" :key="r" class="bar-fill" :style="{ flex: d[r], background: roleColor[r] }"></span>
                </div>
              </div>
              <span class="bar-val">{{ d.users }}</span>
            </div>
          </div>
          <div class="legend">
            <span v-for="r in roleKeys" :key="r"><i :style="{ background: roleColor[r] }"></i>{{ roleLabel(r) }}</span>
          </div>
        </template>
      </div>
    </section>

    <section class="card">
      <div class="card-head">
        <div><h2>Sign-in activity</h2><div class="sub">Share of each company's users who signed in during the last 30 days</div></div>
      </div>
      <div class="card-body">
        <div v-if="loading" class="bars"><div v-for="n in 4" :key="n" class="skel skel-row"></div></div>
        <EmptyState v-else-if="!rows.length" :icon="Building2" title="No companies yet" />
        <div v-else class="bars">
          <div v-for="d in rows" :key="d.id" class="bar-row" :title="`${d.name}: ${d.recent} of ${d.users} users`">
            <span class="bar-label">{{ d.name }}</span>
            <div class="bar-track"><span class="bar-fill" :style="{ width: (d.users ? d.recent / d.users * 100 : 0) + '%', background: 'var(--green)' }"></span></div>
            <span class="bar-val">{{ d.users ? Math.round(d.recent / d.users * 100) + '%' : '—' }}</span>
          </div>
        </div>
      </div>
    </section>
  </div>

  <section class="card mt">
    <div class="card-head"><div><h2>Company breakdown</h2></div></div>
    <div class="table-wrap">
      <table class="table stack breakdown">
        <thead>
          <tr>
            <th>Company</th><th>Status</th><th class="t-right">Users</th><th class="t-right">Dealers</th>
            <th class="t-right">Managers</th><th class="t-right">Pilots</th><th class="t-right">Active 30d</th><th>Last sign-in</th>
          </tr>
        </thead>
        <TableSkeleton v-if="loading" :cols="8" :rows="4" />
        <tbody v-else-if="!rows.length">
          <tr class="table-empty"><td colspan="8"><EmptyState :icon="Building2" title="No companies registered yet" /></td></tr>
        </tbody>
        <tbody v-else>
          <tr v-for="d in pagedRows" :key="d.id">
            <td class="cell-head"><span class="t-primary">{{ d.name }}</span></td>
            <td data-label="Status"><span class="badge" :class="d.status === 'active' ? 'success' : 'danger'"><span class="bdot"></span>{{ d.status === 'active' ? 'Active' : 'Suspended' }}</span></td>
            <td data-label="Users" class="t-right num t-primary">{{ d.users }}</td>
            <td data-label="Dealers" class="t-right num">{{ d.dealer }}</td>
            <td data-label="Managers" class="t-right num">{{ d.manager }}</td>
            <td data-label="Pilots" class="t-right num">{{ d.pilot }}</td>
            <td data-label="Active 30d" class="t-right num">{{ d.recent }}</td>
            <td data-label="Last sign-in" class="nowrap muted" :title="d.lastLogin ? fmtDateTime(d.lastLogin) : ''">{{ d.lastLogin ? relTime(d.lastLogin) : 'Never' }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <Pager :pager="pager" />
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ChartColumn, Building2, Users, LogIn, UserX } from 'lucide-vue-next'
import { getCompanies, getUsers } from '../api'
import { fmt, fmtDateTime, relTime, roleLabel } from '../format'
import { toast } from '../toast'
import PageHeader from '../components/PageHeader.vue'
import StatCard from '../components/StatCard.vue'
import EmptyState from '../components/EmptyState.vue'
import TableSkeleton from '../components/TableSkeleton.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const companies = ref([])
const users = ref([])
const loading = ref(true)
const roleKeys = ['dealer', 'manager', 'pilot']
const roleColor = { dealer: 'var(--role-dealer)', manager: 'var(--role-manager)', pilot: 'var(--role-pilot)' }
const MONTH = 30 * 24 * 3600 * 1000

const rows = computed(() => companies.value.map((c) => {
  const us = users.value.filter((u) => u.company === c.id)
  const logins = us.map((u) => u.last_login).filter(Boolean).sort()
  return {
    id: c.id, name: c.name, status: c.status,
    users: us.length,
    dealer: us.filter((u) => u.role === 'dealer').length,
    manager: us.filter((u) => u.role === 'manager').length,
    pilot: us.filter((u) => u.role === 'pilot').length,
    active: us.filter((u) => u.is_active).length,
    recent: us.filter((u) => u.last_login && Date.now() - new Date(u.last_login) < MONTH).length,
    never: us.filter((u) => !u.last_login).length,
    lastLogin: logins[logins.length - 1] || null,
  }
}).sort((a, b) => b.users - a.users || a.name.localeCompare(b.name)))

const totals = computed(() => rows.value.reduce((t, d) => ({
  users: t.users + d.users, active: t.active + d.active, recent: t.recent + d.recent, never: t.never + d.never,
}), { users: 0, active: 0, recent: 0, never: 0 }))
const maxUsers = computed(() => Math.max(1, ...rows.value.map((d) => d.users)))
const pctText = (n, of) => (of ? Math.round((n / of) * 100) + '%' : '0%')

async function load() {
  try {
    ;[companies.value, users.value] = await Promise.all([getCompanies(), getUsers()])
  } catch (e) {
    toast.error('Could not load company analytics')
  } finally { loading.value = false }
}
onMounted(load)

// pagination (resets to page 1 when search/filters change)
const pager = usePaging(rows)
const pagedRows = pager.rows
</script>

<style scoped>
@media (max-width: 1240px) and (min-width: 721px) {
  .breakdown th, .breakdown td { padding-left: 10px; padding-right: 10px; }
  .breakdown th { letter-spacing: .02em; }
}
</style>
