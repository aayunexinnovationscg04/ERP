<template>
  <div class="topbar">
    <h1>User Management</h1>
    <button class="primary ico" @click="showCreate = !showCreate"><Plus :size="16" /> New user</button>
  </div>

  <div v-if="showCreate" class="card" style="padding:16px;margin-bottom:18px">
    <p class="section-title">Create user</p>
    <div class="formgrid">
      <input v-model="nu.username" placeholder="username" />
      <input v-model="nu.password" type="password" placeholder="password" />
      <select v-model="nu.role">
        <option value="owner">owner</option>
        <option value="manager">manager</option>
        <option value="driver">driver</option>
        <option value="superadmin">superadmin</option>
      </select>
      <select v-model="nu.company">
        <option :value="null">— no company —</option>
        <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
      </select>
      <input v-model="nu.phone" placeholder="phone (optional)" />
      <button class="primary ico" @click="create" :disabled="!nu.username || !nu.password"><Plus :size="16" /> Create</button>
    </div>
    <div v-if="msg" class="muted" style="margin-top:8px">{{ msg }}</div>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Username</th><th>Role</th><th>Company</th><th>Active</th><th>Access</th></tr></thead>
      <tbody v-if="loading">
        <tr v-for="n in 6" :key="n">
          <td colspan="5" style="padding:6px 13px"><div class="skel sk-row" style="margin:0"></div></td>
        </tr>
      </tbody>
      <tbody v-else>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.username }}<div class="muted" style="font-size:12px">{{ u.email }}</div></td>
          <td>
            <select :value="u.role" @change="patch(u, { role: $event.target.value })" style="width:auto">
              <option>owner</option><option>manager</option><option>driver</option><option>superadmin</option>
            </select>
          </td>
          <td>
            <select :value="u.company" @change="patch(u, { company: $event.target.value || null })" style="width:auto">
              <option :value="''">—</option>
              <option v-for="c in companies" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </td>
          <td>
            <input type="checkbox" :checked="u.is_active" @change="patch(u, { is_active: $event.target.checked })" />
          </td>
          <td><router-link :to="`/users/${u.id}/permissions`" class="ico">Tabs &amp; overrides <ChevronRight :size="14" /></router-link></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Plus, ChevronRight } from 'lucide-vue-next'
import { getUsers, createUser, updateUser, getCompanies } from '../api'

const users = ref([]); const companies = ref([])
const loading = ref(true)
const showCreate = ref(false); const msg = ref('')
const nu = ref({ username: '', password: '', role: 'owner', company: null, phone: '' })

async function load() {
  try {
    ;[users.value, companies.value] = await Promise.all([getUsers(), getCompanies()])
  } finally { loading.value = false }
}
async function create() {
  msg.value = ''
  try {
    await createUser({ ...nu.value })
    nu.value = { username: '', password: '', role: 'owner', company: null, phone: '' }
    showCreate.value = false
    await load()
  } catch (e) { msg.value = 'Error: ' + JSON.stringify(e.response?.data || e.message) }
}
async function patch(u, body) {
  await updateUser(u.id, body); await load()
}
onMounted(load)
</script>

<style scoped>
.formgrid { display: grid; grid-template-columns: repeat(3, 1fr) auto; gap: 10px; }
select { font: inherit; background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 9px 10px; border-radius: 8px; }
@media (max-width: 800px) { .formgrid { grid-template-columns: 1fr 1fr; } }
</style>
