<template>
  <div class="topbar">
    <h1>Route History</h1>
    <span class="muted">{{ trips.length }} trip(s)</span>
  </div>

  <div class="card" style="padding:6px 0">
    <table>
      <thead>
        <tr><th>Truck</th><th>Date</th><th class="col-optional">Distance</th><th class="col-optional">Duration</th><th>From</th><th>To</th></tr>
      </thead>
      <tbody>
        <tr v-for="t in trips" :key="t.id">
          <td>
            <span class="row-with-chip">
              <span class="icon-chip blue"><Truck :size="16" /></span>
              <span style="font-weight:600">{{ t.vehicleName }}</span>
            </span>
          </td>
          <td class="muted">{{ t.date }}</td>
          <td class="col-optional">{{ t.distance }} km</td>
          <td class="col-optional">{{ t.duration }}</td>
          <td class="ico"><MapPin :size="13" class="muted" />{{ t.from }}</td>
          <td class="ico"><Flag :size="13" class="muted" />{{ t.to }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { Truck, MapPin, Flag } from 'lucide-vue-next'
import { MOCK_VEHICLES, seededRandom, pick, rangeInt, addDays, fmtDate } from '../mock'

const PLACES = [
  'Depot Yard, Raipur', 'Bhilai Steel Gate', 'Durg Warehouse', 'Rajnandgaon Terminal',
  'Bilaspur Fuel Depot', 'Korba Loading Point', 'Ambikapur Site', 'Jagdalpur Customer Site',
]

const rng = seededRandom(303)
const today = new Date()

const trips = []
let id = 1
for (let i = 0; i < 26; i++) {
  const v = pick(rng, MOCK_VEHICLES)
  const date = addDays(today, -rangeInt(rng, 0, 21))
  const distance = rangeInt(rng, 18, 420)
  const hrs = Math.floor(distance / rangeInt(rng, 30, 45))
  const mins = rangeInt(rng, 5, 55)
  let from = pick(rng, PLACES)
  let to = pick(rng, PLACES)
  if (to === from) to = PLACES[(PLACES.indexOf(from) + 1) % PLACES.length]
  trips.push({
    id: id++, vehicleName: v.name, date: fmtDate(date),
    distance, duration: `${hrs}h ${mins}m`, from, to, sortKey: date.getTime(),
  })
}
trips.sort((a, b) => b.sortKey - a.sortKey)
</script>

<style scoped>
@media (max-width: 720px) {
  .col-optional { display: none; }
  table { min-width: 0; }
}
</style>
