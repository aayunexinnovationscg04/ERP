<template>
  <PageHeader title="ETA & Delivery" :description="`${enroute.length} truck(s) en route with live ETA and recent delivery events.`" preview />

  <div class="eta-grid">
    <div class="card eta-box" v-for="t in enroute" :key="t.id">
      <div class="eta-top">
        <span class="icon-chip blue"><Truck :size="16" /></span>
        <div style="min-width:0">
          <div class="eta-name">{{ t.vehicleName }}</div>
          <div class="eta-dest"><Flag :size="12" /> {{ t.destination }}</div>
        </div>
      </div>
      <div class="eta-countdown num">{{ t.etaLabel }}</div>
      <div class="meter"><span class="brand" :style="{ width: t.progress + '%' }"></span></div>
      <div class="eta-pct">{{ t.progress }}% of route complete</div>
    </div>
  </div>

  <div class="card section">
    <div class="card-head"><div class="card-head-title"><PackageCheck :size="17" /><h2>Delivery timeline</h2></div></div>
    <div class="card-body">
      <div class="tl">
        <div class="tl-row" v-for="ev in timeline" :key="ev.id">
          <span class="tl-dot" :class="ev.cls"></span>
          <div class="tl-body">
            <div class="tl-head"><b>{{ ev.title }}</b><span class="muted">{{ ev.when }}</span></div>
            <div class="muted" style="font-size:12.5px">{{ ev.detail }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Truck, Flag, PackageCheck } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
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
.eta-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 14px; }
.eta-box { padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; }
.eta-top { display: flex; align-items: center; gap: 10px; }
.eta-name { font-weight: 700; font-size: 15px; color: var(--ink-strong); }
.eta-dest { display: flex; align-items: center; gap: 5px; font-size: 12.5px; color: var(--muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.eta-countdown { font-size: 22px; font-weight: 800; letter-spacing: -.01em; color: var(--ink-strong); font-family: var(--font-head); }
.eta-pct { font-size: 12px; color: var(--muted); }
.tl { display: flex; flex-direction: column; }
.tl-row { display: flex; gap: 14px; padding: 10px 0; position: relative; }
.tl-row:not(:last-child)::before { content: ''; position: absolute; left: 4px; top: 24px; bottom: -6px; width: 2px; background: var(--border); }
.tl-dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 5px; flex: none; background: var(--muted-2); }
.tl-dot.blue { background: var(--info); }
.tl-dot.amber { background: var(--amber); }
.tl-dot.green { background: var(--green); }
.tl-body { flex: 1; min-width: 0; }
.tl-head { display: flex; justify-content: space-between; gap: 10px; font-size: 13.5px; }
.tl-head b { color: var(--ink-strong); }
.tl-head span { font-size: 12.5px; white-space: nowrap; }
</style>
