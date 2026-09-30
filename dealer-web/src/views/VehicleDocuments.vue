<template>


  <div v-if="loading" class="kpis"><div class="skel sk-chip" v-for="n in 4" :key="n"></div></div>
  <div v-else class="kpis">
    <StatTile label="Documents" :value="docs.length" :icon="FileText" tone="navy" />
    <StatTile label="Valid" :value="counts.valid" :icon="FileCheck2" tone="green" />
    <StatTile label="Expiring soon" :value="counts.expiring_soon" :icon="FileClock" tone="amber" />
    <StatTile label="Expired" :value="counts.expired" :icon="FileX2" tone="crit" />
  </div>

  <div class="card flush">
    <div class="card-head" v-if="loading || docs.length">
      <div class="toolbar" style="margin:0;flex:1">
        <label class="search">
          <Search :size="16" />
          <input v-model="q" type="search" placeholder="Search vehicle or document…" aria-label="Search documents" />
        </label>
        <div class="chips">
          <button v-for="f in FILTERS" :key="f.key" type="button" class="chip" :class="{ on: filter === f.key }" @click="filter = f.key">
            {{ f.label }} <span class="chip-count">{{ f.key ? (counts[f.key] || 0) : docs.length }}</span>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="card-body"><div class="skel sk-row" v-for="n in 6" :key="n"></div></div>
    <EmptyState v-else-if="!docs.length" :icon="FileText" title="No documents on file" />
    <EmptyState v-else-if="!shown.length" compact :icon="SearchX" title="No matching documents" />
    <div v-else class="table-wrap hide-sm">
      <table>
        <thead><tr><th>Vehicle</th><th>Document</th><th class="hide-sm">Number</th><th>Expires</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="d in pager.rows.value" :key="d.id" class="clickable" @click="$router.push(`/vehicles/${d.vehicleId}`)">
            <td><div class="cell-main">{{ d.vehicleName }}</div><div class="cell-sub">{{ d.vehicleReg }}</div></td>
            <td><span class="ico"><component :is="docIcon(d.doc_type)" :size="15" class="muted" />{{ d.doc_type_label }}</span></td>
            <td class="hide-sm muted">{{ d.number || '—' }}</td>
            <td class="nowrap">{{ d.expiry_date ? fmtDate(d.expiry_date) : '—' }}<div class="cell-sub" v-if="d.expiry_date">{{ relDays(d.expiry_date) }}</div></td>
            <td><span class="badge" :class="BADGE[d.expiry_status]">{{ LABEL[d.expiry_status] }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="!loading && shown.length" class="list show-sm">
      <router-link v-for="d in pager.rows.value" :key="d.id" :to="`/vehicles/${d.vehicleId}`" class="list-row">
        <span class="icon-chip" :class="{ critical: 'crit', idle: 'amber', active: 'green', offline: 'gray' }[BADGE[d.expiry_status]]"><component :is="docIcon(d.doc_type)" :size="16" /></span>
        <span class="grow">
          <div class="title">{{ d.doc_type_label }}</div>
          <div class="sub">{{ d.vehicleName }}<template v-if="d.expiry_date"> · {{ fmtDate(d.expiry_date) }}</template></div>
        </span>
        <span class="badge" :class="BADGE[d.expiry_status]">{{ LABEL[d.expiry_status] }}</span>
      </router-link>
    </div>
    <Pager v-if="!loading && shown.length" :pager="pager" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  FileText, ShieldCheck, ClipboardCheck, BadgeCheck, Leaf, FileCheck2, FileClock, FileX2, Search, SearchX,
} from 'lucide-vue-next'
import { getVehicles } from '../api'
import StatTile from '../components/StatTile.vue'
import EmptyState from '../components/EmptyState.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'

const LABEL = { valid: 'Valid', expiring_soon: 'Expiring soon', expired: 'Expired', unknown: 'No expiry set' }
const BADGE = { valid: 'active', expiring_soon: 'idle', expired: 'critical', unknown: 'offline' }
const ORDER = { expired: 0, expiring_soon: 1, unknown: 2, valid: 3 }
const ICONS = { rc: FileText, insurance: ShieldCheck, permit: ClipboardCheck, fitness: BadgeCheck, puc: Leaf }
const FILTERS = [
  { key: '', label: 'All' },
  { key: 'expired', label: 'Expired' },
  { key: 'expiring_soon', label: 'Expiring' },
  { key: 'valid', label: 'Valid' },
]
function docIcon(t) { return ICONS[t] || FileText }

const vehicles = ref([])
const loading = ref(true)
const q = ref('')
const filter = ref('')

const docs = computed(() => vehicles.value.flatMap((v) => (v.documents || []).map((d) => ({
  ...d, vehicleId: v.id, vehicleName: v.local_name, vehicleReg: v.registration_number,
}))).sort((a, b) => (ORDER[a.expiry_status] - ORDER[b.expiry_status]) || String(a.expiry_date).localeCompare(String(b.expiry_date))))
const counts = computed(() => {
  const c = { valid: 0, expiring_soon: 0, expired: 0, unknown: 0 }
  docs.value.forEach((d) => { c[d.expiry_status] = (c[d.expiry_status] || 0) + 1 })
  return c
})
const shown = computed(() => {
  const t = q.value.trim().toLowerCase()
  return docs.value.filter((d) => (!filter.value || d.expiry_status === filter.value) &&
    (!t || [d.vehicleName, d.vehicleReg, d.doc_type_label, d.number].some((x) => x?.toLowerCase().includes(t))))
})

const pager = usePaging(shown, 10, [q, filter])

function fmtDate(s) { return new Date(s + 'T00:00:00').toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) }
function relDays(s) {
  const days = Math.round((new Date(s + 'T00:00:00') - new Date(new Date().toDateString())) / 86400000)
  if (days === 0) return 'today'
  return days > 0 ? `in ${days} day${days === 1 ? '' : 's'}` : `${-days} day${days === -1 ? '' : 's'} ago`
}

onMounted(async () => {
  try { vehicles.value = await getVehicles() } catch (e) { /* empty */ }
  finally { loading.value = false }
})
</script>
