<template>
  <div class="topbar">
    <div class="heading">
      <span class="eyebrow">Platform / User Management</span>
      <h1>Users</h1>
    </div>
    <button class="primary ico" style="width:auto" @click="showCreate = !showCreate"><Plus :size="16" /> New user</button>
  </div>

  <div class="chiprow" v-if="!loading">
    <div class="chip" style="border-top-color:var(--brand)"><span class="chip-n num">{{ users.length }}</span><span class="chip-l">Total users</span></div>
    <div class="chip" style="border-top-color:var(--green)"><span class="chip-n num">{{ activeCount }}</span><span class="chip-l">Active now</span></div>
    <div class="chip" style="border-top-color:var(--role-manager)"><span class="chip-n num">{{ roleCounts.length }}</span><span class="chip-l">Roles in use</span></div>
  </div>

  <AnimatePresence>
    <motion.div
      v-if="showCreate" class="card users-card" style="padding:16px;margin-bottom:18px"
      :initial="{ opacity: 0, height: 0 }" :animate="{ opacity: 1, height: 'auto' }" :exit="{ opacity: 0, height: 0 }"
      :transition="{ duration: 0.18, ease: [0.4, 0, 0.2, 1] }"
    >
      <p class="section-title">Create user</p>
      <div class="formgrid">
        <input v-model="nu.username" placeholder="username" />
        <input v-model="nu.password" type="password" placeholder="password" />
        <select v-model="nu.role">
          <option value="dealer">Dealer</option>
          <option value="manager">Manager</option>
          <option value="pilot">Pilot</option>
          <option value="admin">Admin</option>
        </select>
        <select v-model="nu.company">
          <option :value="null">— no company —</option>
          <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <input v-model="nu.phone" placeholder="phone (optional)" />
        <button class="primary ico" style="width:auto" @click="create" :disabled="!nu.username || !nu.password"><Plus :size="16" /> Create</button>
      </div>
      <div v-if="msg" class="muted" style="margin-top:8px">{{ msg }}</div>
    </motion.div>
  </AnimatePresence>

  <div class="card users-card" style="padding:6px 0">
    <table>
      <thead><tr><th>Username</th><th>Role</th><th>Company</th><th>Active</th><th>Access</th></tr></thead>
      <tbody v-if="loading">
        <tr v-for="n in 6" :key="n">
          <td colspan="5" style="padding:6px 13px"><div class="skel sk-row" style="margin:0"></div></td>
        </tr>
      </tbody>
      <tbody v-else>
        <motion.tr
          v-for="(u, idx) in users" :key="u.id"
          :initial="{ opacity: 0, y: 6 }" :animate="{ opacity: 1, y: 0 }"
          :transition="{ duration: 0.16, delay: Math.min(idx, 10) * 0.02, ease: [0.4, 0, 0.2, 1] }"
        >
          <td>{{ u.username }}<div class="muted" style="font-size:12px">{{ u.email }}</div></td>
          <td>
            <select :value="u.role" class="role-select" :class="'r-' + u.role" @change="patch(u, { role: $event.target.value })" style="width:auto">
              <option value="dealer">Dealer</option>
              <option value="manager">Manager</option>
              <option value="pilot">Pilot</option>
              <option value="admin">Admin</option>
            </select>
          </td>
          <td>
            <select :value="u.company" @change="patch(u, { company: $event.target.value || null })" style="width:auto">
              <option :value="''">—</option>
              <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </td>
          <td>
            <ToggleSwitch :model-value="u.is_active" @change="(v) => patch(u, { is_active: v })" />
          </td>
          <td><router-link :to="`/users/${u.id}/permissions`" class="tabs-link"><SlidersHorizontal :size="13" /> Tabs &amp; overrides</router-link></td>
        </motion.tr>
      </tbody>
    </table>
    <div v-if="!loading" class="table-foot">{{ users.length }} {{ users.length === 1 ? 'user' : 'users' }} total</div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { motion, AnimatePresence } from 'motion-v'
import { Plus, SlidersHorizontal } from 'lucide-vue-next'
import { getUsers, createUser, updateUser, getCompanies } from '../api'
import { toast } from '../toast'
import ToggleSwitch from '../components/ToggleSwitch.vue'

const users = ref([]); const companies = ref([])
const loading = ref(true)
const showCreate = ref(false); const msg = ref('')
const nu = ref({ username: '', password: '', role: 'dealer', company: null, phone: '' })

const activeCount = computed(() => users.value.filter((u) => u.is_active).length)
const roleCounts = computed(() => [...new Set(users.value.map((u) => u.role))])

async function load() {
  try {
    ;[users.value, companies.value] = await Promise.all([getUsers(), getCompanies()])
  } finally { loading.value = false }
}
async function create() {
  msg.value = ''
  try {
    await createUser({ ...nu.value })
    nu.value = { username: '', password: '', role: 'dealer', company: null, phone: '' }
    showCreate.value = false
    await load()
    toast.success('User created')
  } catch (e) {
    msg.value = 'Error: ' + JSON.stringify(e.response?.data || e.message)
    toast.error('Could not create user')
  }
}
async function patch(u, body) {
  try {
    await updateUser(u.id, body); await load()
    toast.success('User updated')
  } catch (e) {
    await load()
    toast.error('Could not update user')
  }
}
onMounted(load)
</script>

<style scoped>
/* cap the table card's width so a handful of demo rows reads as a
   deliberately-sized panel rather than a mostly-empty full-bleed table
   stretched across the whole content column */
.users-card { max-width: 980px; }
.formgrid { display: grid; grid-template-columns: repeat(3, 1fr) auto; gap: 10px; }
select { font: inherit; background: var(--surface-2); border: 1px solid var(--border); color: var(--text); padding: 9px 10px; border-radius: 8px; }
.role-select { font-weight: 700; font-size: 12.5px; }
.role-select.r-admin { background: var(--role-admin-soft); color: var(--role-admin); border-color: rgba(139,92,246,.35); }
.role-select.r-dealer { background: var(--role-dealer-soft); color: var(--role-dealer); border-color: rgba(245,158,11,.35); }
.role-select.r-manager { background: var(--role-manager-soft); color: var(--role-manager); border-color: rgba(45,212,191,.35); }
.role-select.r-pilot { background: var(--role-pilot-soft); color: var(--role-pilot); border-color: rgba(56,189,248,.35); }
@media (max-width: 800px) { .formgrid { grid-template-columns: 1fr 1fr; } }
</style>
