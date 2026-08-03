<template>
  <div class="topbar">
    <h1>Vehicle Documents</h1>
    <span class="muted">{{ docs.length }} document(s)</span>
  </div>

  <div class="kpis">
    <motion.div class="card kpi glow-green" :while-hover="{ y: -2 }">
      <span class="icon-chip lg green ic"><FileCheck2 :size="20" class="icon-lg" /></span><div class="n">{{ counts.valid }}</div><div class="l">Valid</div>
    </motion.div>
    <motion.div class="card kpi glow-amber" :while-hover="{ y: -2 }">
      <span class="icon-chip lg amber ic"><FileClock :size="20" class="icon-lg" /></span><div class="n">{{ counts.expiring }}</div><div class="l">Expiring soon</div>
    </motion.div>
    <motion.div class="card kpi glow-crit" :while-hover="{ y: -2 }">
      <span class="icon-chip lg crit ic"><FileX2 :size="20" class="icon-lg" /></span><div class="n">{{ counts.expired }}</div><div class="l">Expired</div>
    </motion.div>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead><tr><th>Truck</th><th>Document type</th><th>Expiry date</th><th>Status</th></tr></thead>
      <tbody>
        <tr v-for="d in docs" :key="d.id" :class="d.rowClass">
          <td>
            <div style="font-weight:600">{{ d.vehicleName }}</div>
            <div class="muted" style="font-size:12px">{{ d.vehicleReg }}</div>
          </td>
          <td class="ico"><component :is="d.icon" :size="14" class="muted" />{{ d.docType }}</td>
          <td class="muted">{{ d.expiryDate }}</td>
          <td><span class="badge" :class="d.rowClass">{{ d.statusLabel }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { FileText, ShieldCheck, ClipboardCheck, BadgeCheck, Leaf, FileCheck2, FileClock, FileX2 } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_VEHICLES, seededRandom, addDays, fmtDate } from '../mock'

const DOC_TYPES = [
  { key: 'rc', label: 'RC (Registration Certificate)', icon: FileText },
  { key: 'insurance', label: 'Insurance', icon: ShieldCheck },
  { key: 'permit', label: 'Permit', icon: ClipboardCheck },
  { key: 'fitness', label: 'Fitness Certificate', icon: BadgeCheck },
  { key: 'puc', label: 'PUC (Pollution)', icon: Leaf },
]

const rng = seededRandom(202)
const today = new Date()

const docs = []
let id = 1
for (const v of MOCK_VEHICLES) {
  for (const type of DOC_TYPES) {
    const roll = rng()
    // weighted: mostly valid, some expiring soon, a few expired
    const offsetDays = roll < 0.65 ? Math.round(30 + rng() * 300)
      : roll < 0.85 ? Math.round(rng() * 25)
      : -Math.round(1 + rng() * 60)
    const expiry = addDays(today, offsetDays)
    let status, rowClass, statusLabel
    if (offsetDays < 0) { status = 'expired'; rowClass = 'critical'; statusLabel = 'Expired' }
    else if (offsetDays <= 30) { status = 'expiring'; rowClass = 'warning'; statusLabel = 'Expiring soon' }
    else { status = 'valid'; rowClass = 'active'; statusLabel = 'Valid' }
    docs.push({
      id: id++,
      vehicleName: v.name,
      vehicleReg: v.reg,
      docType: type.label,
      icon: type.icon,
      expiryDate: fmtDate(expiry),
      status, rowClass, statusLabel,
    })
  }
}

const counts = computed(() => ({
  valid: docs.filter((d) => d.status === 'valid').length,
  expiring: docs.filter((d) => d.status === 'expiring').length,
  expired: docs.filter((d) => d.status === 'expired').length,
}))
</script>
