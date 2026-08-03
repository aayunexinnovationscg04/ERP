<template>
  <div class="topbar">
    <h1>ETA &amp; Delivery</h1>
    <span class="muted">{{ enroute.length }} truck(s) en route</span>
  </div>

  <p class="section-title">Live ETA</p>
  <div class="eta-grid">
    <motion.div class="card eta-box" v-for="(t, i) in enroute" :key="t.id"
                :initial="{ opacity: 0, y: 10 }" :animate="{ opacity: 1, y: 0 }"
                :transition="{ duration: .22, delay: Math.min(i, 12) * .03, ease: [.4, 0, .2, 1] }">
      <div class="eta-top">
        <span class="icon-chip blue"><Truck :size="16" /></span>
        <span class="eta-name">{{ t.vehicleName }}</span>
      </div>
      <div class="muted eta-dest"><Flag :size="12" class="pilot-ic" /> {{ t.destination }}</div>
      <div class="eta-countdown">{{ t.etaLabel }}</div>
      <div class="eta-bar"><div class="eta-bar-fill" :style="{ width: t.progress + '%' }"></div></div>
      <div class="muted eta-pct">{{ t.progress }}% of route complete</div>
    </motion.div>
  </div>

  <p class="section-title">Delivery Timeline</p>
  <div class="card" style="padding:16px 20px">
    <div class="tl">
      <div class="tl-row" v-for="ev in timeline" :key="ev.id">
        <span class="tl-dot" :class="ev.cls"></span>
        <div class="tl-body">
          <div class="tl-head">
            <b>{{ ev.title }}</b>
            <span class="muted">{{ ev.when }}</span>
          </div>
          <div class="muted" style="font-size:12.5px">{{ ev.detail }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Truck, Flag } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { MOCK_VEHICLES, MOCK_CUSTOMERS, seededRandom, pick, rangeInt } from '../mock'

const rng = seededRandom(1212)

const enroute = MOCK_VEHICLES.slice(0, 5).map((v, i) => {
  const progress = rangeInt(rng, 12, 92)
  const mins = Math.round((100 - progress) * rangeInt(rng, 2, 5))
  const etaLabel = mins >= 60 ? `${Math.floor(mins / 60)}h ${mins % 60}m` : `${mins}m`
  return { id: v.id, vehicleName: v.name, destination: pick(rng, MOCK_CUSTOMERS), progress, etaLabel: `ETA ${etaLabel}` }
})

const EVENT_TEMPLATES = [
  { title: 'Order dispatched', cls: 'blue' },
  { title: 'Departed depot', cls: 'blue' },
  { title: 'In transit', cls: 'amber' },
  { title: 'Arrived at checkpoint', cls: 'amber' },
  { title: 'Delivered', cls: 'green' },
]
const timeline = Array.from({ length: 8 }, (_, i) => {
  const v = pick(rng, MOCK_VEHICLES)
  const tpl = pick(rng, EVENT_TEMPLATES)
  const minsAgo = rangeInt(rng, 4, 340) + i * 20
  return {
    id: i + 1, title: tpl.title, cls: tpl.cls,
    detail: `${v.name} · ${pick(rng, MOCK_CUSTOMERS)}`,
    when: minsAgo < 60 ? `${minsAgo}m ago` : `${Math.round(minsAgo / 60)}h ago`,
    sortKey: minsAgo,
  }
}).sort((a, b) => a.sortKey - b.sortKey)
</script>

<style scoped>
.eta-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 14px; margin-bottom: 4px; }
.eta-box { padding: 18px 20px; display: flex; flex-direction: column; gap: 6px; }
.eta-top { display: flex; align-items: center; gap: 10px; }
.eta-name { font-weight: 700; font-size: 15px; color: var(--ink-strong); }
.eta-dest { display: flex; align-items: center; gap: 5px; font-size: 12.5px; }
.eta-countdown { font-size: 24px; font-weight: 800; letter-spacing: -.01em; color: var(--brand); font-family: var(--font-head); margin-top: 2px; }
.eta-bar { height: 6px; border-radius: 999px; background: var(--surface-2); overflow: hidden; margin-top: 4px; }
.eta-bar-fill { height: 100%; background: var(--accent-grad); border-radius: 999px; transition: width var(--dur) var(--ease); }
.eta-pct { font-size: 11.5px; margin-top: 2px; }

.tl { display: flex; flex-direction: column; }
.tl-row { display: flex; gap: 14px; padding: 10px 0; position: relative; }
.tl-row:not(:last-child)::before { content: ''; position: absolute; left: 4px; top: 22px; bottom: -4px; width: 1px; background: var(--border); }
.tl-dot { width: 9px; height: 9px; border-radius: 50%; margin-top: 5px; flex: none; background: var(--gray); }
.tl-dot.blue { background: var(--blue); }
.tl-dot.amber { background: var(--amber); }
.tl-dot.green { background: var(--green); }
.tl-body { flex: 1; }
.tl-head { display: flex; justify-content: space-between; gap: 10px; font-size: 14px; }
</style>
