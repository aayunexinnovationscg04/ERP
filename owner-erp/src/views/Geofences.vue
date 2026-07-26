<template>
  <div class="topbar">
    <h1>Geofences</h1>
    <button class="primary ico" @click="toggleCreate">
      <component :is="createMode ? X : Plus" :size="16" />
      {{ createMode ? 'Cancel' : 'New zone' }}
    </button>
  </div>

  <!-- loading skeleton -->
  <div v-if="loading" class="grid-2">
    <div><div class="skel sk-map"></div></div>
    <div>
      <p class="section-title">Zones</p>
      <div class="skel sk-row" v-for="n in 5" :key="n"></div>
    </div>
  </div>

  <div v-else class="grid-2">
    <!-- MAP + create controls -->
    <div>
      <div v-if="createMode" class="card" style="padding:14px 16px; margin-bottom:14px">
        <p class="section-title" style="margin-top:0">New circular zone</p>
        <p class="muted ico" style="font-size:13px; margin:0 0 12px">
          <MapPin :size="15" />
          {{ draft.lat == null ? 'Click the map to drop the zone centre.' : 'Drag the marker or click again to move the centre.' }}
        </p>
        <div class="gf-form">
          <label>
            <span class="muted">Name</span>
            <input v-model="draft.name" placeholder="e.g. Depot yard" />
          </label>
          <label>
            <span class="muted">Radius (m)</span>
            <input v-model.number="draft.radius_m" type="number" min="10" step="10" />
          </label>
          <label>
            <span class="muted">Purpose</span>
            <select v-model="draft.purpose">
              <option value="allowed">Allowed</option>
              <option value="restricted">Restricted</option>
              <option value="customer_site">Customer site</option>
            </select>
          </label>
        </div>
        <div class="row" style="margin-top:12px">
          <button class="primary ico" :disabled="!canSave || saving" @click="save">
            <Save :size="16" /> {{ saving ? 'Saving…' : 'Save zone' }}
          </button>
          <span v-if="saveErr" class="err" style="margin:0">{{ saveErr }}</span>
        </div>
      </div>

      <div ref="mapEl" class="map"></div>

      <div class="row" style="gap:16px; margin-top:10px; flex-wrap:wrap">
        <span class="ico muted" style="font-size:12px"><i class="gf-swatch" style="background:#16a34a"></i> Allowed</span>
        <span class="ico muted" style="font-size:12px"><i class="gf-swatch" style="background:#dc2626"></i> Restricted</span>
        <span class="ico muted" style="font-size:12px"><i class="gf-swatch" style="background:#2563eb"></i> Customer site</span>
      </div>
    </div>

    <!-- LIST -->
    <div>
      <p class="section-title">Zones ({{ zones.length }})</p>

      <div v-if="!zones.length" class="card empty">
        <MapPin :size="30" :stroke-width="1.75" style="color:var(--muted)" />
        <div style="margin-top:8px">No zones yet.</div>
        <div class="muted" style="font-size:13px; margin-top:4px">
          Use “New zone” to draw your first geofence on the map.
        </div>
      </div>

      <div v-else class="card" style="padding:6px 0">
        <table>
          <tbody>
            <tr v-for="z in zones" :key="z.id" class="clickable" @click="focusZone(z)">
              <td>
                <div style="font-weight:600">{{ z.name }}</div>
                <div class="muted" style="font-size:12px">
                  {{ z.kind }}<span v-if="z.kind === 'circle' && z.radius_m"> · {{ Math.round(z.radius_m) }} m</span>
                </div>
              </td>
              <td><span class="badge" :style="badgeStyle(z.purpose)">{{ purposeLabel(z.purpose) }}</span></td>
              <td @click.stop>
                <button class="ico" :class="{ primary: z.active }" @click="toggleActive(z)">
                  <component :is="z.active ? Eye : EyeOff" :size="15" />
                  {{ z.active ? 'Active' : 'Off' }}
                </button>
              </td>
              <td @click.stop style="text-align:right">
                <button class="ico" @click="remove(z)"><Trash2 :size="15" /></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import { Plus, X, Save, MapPin, Trash2, Eye, EyeOff } from 'lucide-vue-next'
import { getGeofences, createGeofence, updateGeofence, deleteGeofence } from '../api'

const PURPOSE = {
  allowed:       { label: 'Allowed',       color: '#16a34a', soft: 'rgba(22,163,74,.14)' },
  restricted:    { label: 'Restricted',    color: '#dc2626', soft: 'rgba(220,38,38,.14)' },
  customer_site: { label: 'Customer site', color: '#2563eb', soft: 'rgba(37,99,235,.14)' },
}
function purposeColor(p) { return PURPOSE[p]?.color || '#7a6c5d' }
function purposeLabel(p) { return PURPOSE[p]?.label || p }
function badgeStyle(p) {
  const m = PURPOSE[p]
  return m ? `background:${m.soft};color:${m.color}` : ''
}

const loading = ref(true)
const zones = ref([])
const createMode = ref(false)
const saving = ref(false)
const saveErr = ref('')
const draft = ref({ name: '', radius_m: 300, purpose: 'allowed', lat: null, lng: null })

const mapEl = ref(null)
let map, zoneLayer, draftLayer, draftMarker, draftCircle
const boundsById = {}

const canSave = computed(() =>
  draft.value.lat != null && draft.value.radius_m > 0 && draft.value.name.trim().length > 0)

function drawZones() {
  if (!map) return
  zoneLayer.clearLayers()
  const all = []
  zones.value.forEach((z) => {
    const color = purposeColor(z.purpose)
    const opts = { color, weight: 2, fillColor: color, fillOpacity: z.active ? 0.18 : 0.06, dashArray: z.active ? null : '5,5' }
    let layer = null
    if (z.kind === 'circle' && z.center_lat != null && z.radius_m) {
      layer = L.circle([z.center_lat, z.center_lng], { radius: z.radius_m, ...opts })
    } else if (z.kind === 'polygon' && Array.isArray(z.polygon) && z.polygon.length) {
      const latlngs = z.polygon.map((p) => Array.isArray(p) ? [p[0], p[1]] : [p.lat, p.lng])
      layer = L.polygon(latlngs, opts)
    }
    if (!layer) return
    layer.bindTooltip(`${z.name} · ${purposeLabel(z.purpose)}`)
    layer.addTo(zoneLayer)
    const b = layer.getBounds()
    boundsById[z.id] = b
    if (b.isValid()) all.push(b)
  })
  if (all.length) {
    const total = all.reduce((acc, b) => acc.extend(b), L.latLngBounds(all[0].getSouthWest(), all[0].getNorthEast()))
    map.fitBounds(total.pad(0.2), { maxZoom: 15 })
  }
}

function focusZone(z) {
  const b = boundsById[z.id]
  if (b && b.isValid()) map.fitBounds(b.pad(0.4), { maxZoom: 16 })
}

function updateDraftPreview() {
  if (!map) return
  draftLayer.clearLayers()
  draftMarker = null
  draftCircle = null
  if (draft.value.lat == null) return
  const ll = [draft.value.lat, draft.value.lng]
  const color = purposeColor(draft.value.purpose)
  draftCircle = L.circle(ll, { radius: draft.value.radius_m || 1, color, weight: 2, fillColor: color, fillOpacity: 0.2 }).addTo(draftLayer)
  draftMarker = L.marker(ll, { draggable: true }).addTo(draftLayer)
  draftMarker.on('drag', (e) => {
    const p = e.target.getLatLng()
    draft.value.lat = p.lat; draft.value.lng = p.lng
    if (draftCircle) draftCircle.setLatLng(p)
  })
}

function toggleCreate() {
  createMode.value = !createMode.value
  saveErr.value = ''
  if (!createMode.value) {
    draft.value = { name: '', radius_m: 300, purpose: 'allowed', lat: null, lng: null }
    if (draftLayer) draftLayer.clearLayers()
  }
}

async function save() {
  if (!canSave.value) return
  saving.value = true; saveErr.value = ''
  try {
    await createGeofence({
      name: draft.value.name.trim(),
      kind: 'circle',
      center_lat: draft.value.lat,
      center_lng: draft.value.lng,
      radius_m: draft.value.radius_m,
      purpose: draft.value.purpose,
      active: true,
    })
    toggleCreate()
    await load()
  } catch (e) {
    saveErr.value = e.response?.data?.detail || 'Could not save zone.'
  } finally {
    saving.value = false
  }
}

async function toggleActive(z) {
  const next = !z.active
  try {
    await updateGeofence(z.id, { active: next })
    z.active = next
    drawZones()
  } catch (e) { /* ignore */ }
}

async function remove(z) {
  if (!confirm(`Delete zone “${z.name}”? This cannot be undone.`)) return
  try {
    await deleteGeofence(z.id)
    zones.value = zones.value.filter((x) => x.id !== z.id)
    delete boundsById[z.id]
    drawZones()
  } catch (e) { /* ignore */ }
}

async function load() {
  try {
    zones.value = await getGeofences()
  } catch (e) { /* keep last good data */ }
  finally { loading.value = false }
  // draw after the map element exists (v-if swaps skeleton -> map)
  await nextTick()
  initMap()
  drawZones()
  updateDraftPreview()
}

function initMap() {
  if (map || !mapEl.value) return
  map = L.map(mapEl.value, { zoomControl: true }).setView([21.145, 81.664], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap', maxZoom: 19,
  }).addTo(map)
  zoneLayer = L.layerGroup().addTo(map)
  draftLayer = L.layerGroup().addTo(map)
  map.on('click', (e) => {
    if (!createMode.value) return
    draft.value.lat = e.latlng.lat
    draft.value.lng = e.latlng.lng
    updateDraftPreview()
  })
}

// keep the live circle preview in sync with radius / purpose edits
watch(() => [draft.value.radius_m, draft.value.purpose], () => {
  if (!createMode.value || draft.value.lat == null || !draftCircle) return
  draftCircle.setRadius(draft.value.radius_m || 1)
  const color = purposeColor(draft.value.purpose)
  draftCircle.setStyle({ color, fillColor: color })
})

onMounted(load)
onBeforeUnmount(() => { if (map) map.remove() })
</script>

<style scoped>
.gf-form { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 12px; }
.gf-form label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 600; }
.gf-form label:first-child { grid-column: 1 / -1; }
.gf-form select {
  font: inherit; width: 100%; color: var(--text);
  background: var(--surface); border: 1px solid var(--border);
  padding: 13px 14px; border-radius: var(--radius-sm);
}
.gf-swatch { width: 11px; height: 11px; border-radius: 3px; display: inline-block; }
</style>
