<template>
  <PageHeader>
    <button v-if="canWrite" :class="createMode ? '' : 'primary'" @click="toggleCreate">
      <component :is="createMode ? X : Plus" :size="16" />
      {{ createMode ? 'Cancel' : 'New zone' }}
    </button>
  </PageHeader>

  <div v-if="loading" class="grid-2">
    <div class="skel sk-map"></div>
    <div class="card card-body"><div class="skel sk-row" v-for="n in 5" :key="n"></div></div>
  </div>

  <div v-else class="grid-2">
    <div class="stack">
      <div v-if="createMode" class="card gf-create">
        <div class="card-head">
          <div class="card-head-title"><CircleDashed :size="17" /><h2>New zone</h2></div>
          <span class="badge" :class="draft.lat == null ? 'idle' : 'active'">{{ draft.lat == null ? 'Tap map to set centre' : 'Centre set' }}</span>
        </div>
        <div class="card-body">
          <div class="gf-form">
            <label class="field gf-name">
              <span>Zone name</span>
              <input v-model="draft.name" placeholder="e.g. Depot yard" maxlength="80" />
            </label>
            <label class="field">
              <span>Radius (metres)</span>
              <input v-model.number="draft.radius_m" type="number" min="10" step="10" inputmode="numeric" />
            </label>
            <label class="field">
              <span>Purpose</span>
              <select v-model="draft.purpose">
                <option value="allowed">Allowed</option>
                <option value="restricted">Restricted</option>
                <option value="customer_site">Customer site</option>
              </select>
            </label>
          </div>
          <div class="row wrap" style="margin-top:14px">
            <button class="primary" :disabled="!canSave || saving" @click="save">
              <Save :size="16" /> {{ saving ? 'Saving…' : 'Save zone' }}
            </button>
            <span v-if="saveErr" class="err">{{ saveErr }}</span>
          </div>
        </div>
      </div>

      <div class="card flush">
        <div class="card-head">
          <div class="card-head-title"><MapIcon :size="17" /><h2>Zone map</h2></div>
          <div class="map-legend">
            <span><i class="swatch" :style="{ background: PURPOSE.allowed.color }"></i>Allowed</span>
            <span><i class="swatch" :style="{ background: PURPOSE.restricted.color }"></i>Restricted</span>
            <span><i class="swatch" :style="{ background: PURPOSE.customer_site.color }"></i>Customer site</span>
          </div>
        </div>
        <div ref="mapEl" class="map" :class="{ picking: createMode }"></div>
      </div>
    </div>

    <div class="card flush">
      <div class="card-head">
        <div class="card-head-title"><MapPin :size="17" /><h2>Zones</h2></div>
        <span v-if="zones.length" class="muted" style="font-size:12.5px">{{ zones.filter((z) => z.active).length }} / {{ zones.length }} on</span>
      </div>

      <EmptyState v-if="!zones.length" :icon="MapPin" title="No zones yet"
        :text="canWrite ? '' : ''">
        <button v-if="canWrite && !createMode" class="primary" @click="toggleCreate"><Plus :size="16" /> New zone</button>
      </EmptyState>

      <div v-else class="list">
        <div v-for="z in pager.rows.value" :key="z.id" class="list-row clickable gf-row" role="button" tabindex="0"
             @click="focusZone(z)" @keydown.enter="focusZone(z)">
          <span class="icon-chip" :class="purposeChip(z.purpose)"><component :is="purposeIcon(z.purpose)" :size="16" /></span>
          <span class="grow">
            <div class="title">{{ z.name }}</div>
            <div class="sub">{{ purposeLabel(z.purpose) }} · {{ z.kind }}<span v-if="z.kind === 'circle' && z.radius_m"> · {{ Math.round(z.radius_m) }} m</span></div>
          </span>
          <template v-if="canWrite">
            <button type="button" class="sm gf-toggle" :class="{ on: z.active }" :title="z.active ? 'Turn zone off' : 'Turn zone on'"
                    role="switch" :aria-checked="z.active" @click.stop="toggleActive(z)">
              <span class="sw"><span></span></span>{{ z.active ? 'On' : 'Off' }}
            </button>
            <button type="button" class="ghost icon-btn sm gf-del" title="Delete zone" aria-label="Delete zone" @click.stop="confirmDel = z"><Trash2 :size="15" /></button>
          </template>
          <span v-else class="badge" :class="z.active ? 'active' : 'off'">{{ z.active ? 'Active' : 'Off' }}</span>
        </div>
      </div>
      <Pager v-if="zones.length" :pager="pager" />
    </div>
  </div>

  <Modal v-if="confirmDel" title="Delete zone?" @close="confirmDel = null">
    <p style="margin:0">“<b>{{ confirmDel.name }}</b>” will be removed. This cannot be undone.</p>
    <template #footer>
      <button type="button" @click="confirmDel = null">Cancel</button>
      <button type="button" class="danger-solid" @click="remove(confirmDel)"><Trash2 :size="15" /> Delete</button>
    </template>
  </Modal>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import L from '../leaflet'
import { Plus, X, Save, MapPin, Trash2, ShieldCheck, Ban, Building2, CircleDashed, Map as MapIcon } from 'lucide-vue-next'
import PageHeader from '../components/PageHeader.vue'
import EmptyState from '../components/EmptyState.vue'
import Modal from '../components/Modal.vue'
import Pager from '../components/Pager.vue'
import { usePaging } from '../paging'
import { getGeofences, createGeofence, updateGeofence, deleteGeofence } from '../api'
import { auth } from '../auth'
import { TILE_URL, TILE_ATTRIBUTION, TILE_SUBDOMAINS } from '../tiles'
import { toast } from '../toast'

const canWrite = computed(() => auth.user?.may_write !== false)

// Leaflet needs literal colors — these are the shared palette values
// (green / red / sky from tokens.css), readable on light and dimmed tiles.
const PURPOSE = {
  allowed:       { label: 'Allowed',       color: '#059669' },
  restricted:    { label: 'Restricted',    color: '#DC2626' },
  customer_site: { label: 'Customer site', color: '#0284C7' },
}
function purposeColor(p) { return PURPOSE[p]?.color || '#64748B' }
function purposeLabel(p) { return PURPOSE[p]?.label || p }
// Row identity by purpose — an "allowed" zone and a "restricted" one should
// not look like the same pin with only the badge text differing.
const PURPOSE_ICON = { allowed: ShieldCheck, restricted: Ban, customer_site: Building2 }
const PURPOSE_CHIP = { allowed: 'green', restricted: 'red', customer_site: 'blue' }
function purposeIcon(p) { return PURPOSE_ICON[p] || MapPin }
function purposeChip(p) { return PURPOSE_CHIP[p] || 'gray' }

const loading = ref(true)
const zones = ref([])
const pager = usePaging(zones, 10)
const createMode = ref(false)
const saving = ref(false)
const saveErr = ref('')
const confirmDel = ref(null)
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
    map.fitBounds(total.pad(0.2), { maxZoom: 15, animate: false })
  }
}

function focusZone(z) {
  if (!map) return
  if (matchMedia('(max-width: 1199px)').matches) mapEl.value?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  const b = boundsById[z.id]
  if (b && b.isValid()) map.fitBounds(b.pad(0.4), { maxZoom: 16, animate: false })
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
    toast.success('Zone saved')
  } catch (e) {
    saveErr.value = e.response?.data?.detail || 'Could not save zone.'
    toast.error('Could not save zone')
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
    toast.success('Zone updated')
  } catch (e) { toast.error('Could not update zone') }
}

async function remove(z) {
  confirmDel.value = null
  try {
    await deleteGeofence(z.id)
    zones.value = zones.value.filter((x) => x.id !== z.id)
    delete boundsById[z.id]
    drawZones()
    toast.success('Zone deleted')
  } catch (e) { toast.error('Could not delete zone') }
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
  map = L.map(mapEl.value, { zoomControl: true }).setView([21.145, 79.088], 12)
  L.tileLayer(TILE_URL, { subdomains: TILE_SUBDOMAINS, maxZoom: 20, attribution: TILE_ATTRIBUTION }).addTo(map)
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
onBeforeUnmount(() => { if (map) { map.stop(); map.off(); map.remove(); map = null } })
</script>
<style scoped>
.gf-form { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.gf-name { grid-column: 1 / -1; }
.map.picking { cursor: crosshair; }
.map.picking :deep(.leaflet-container), .map.picking:deep(.leaflet-grab) { cursor: crosshair; }
.gf-toggle { gap: 8px; min-width: 76px; justify-content: flex-start; }
.sw { width: 28px; height: 16px; border-radius: 999px; background: var(--border-strong); position: relative; flex: none; transition: background var(--dur) var(--ease); }
.sw span { position: absolute; top: 2px; left: 2px; width: 12px; height: 12px; border-radius: 50%; background: #FFFFFF; transition: transform var(--dur) var(--ease); }
.gf-toggle.on .sw { background: var(--green); }
.gf-toggle.on .sw span { transform: translateX(12px); }
.gf-row .title, .gf-row .sub { white-space: normal; overflow-wrap: anywhere; }
.gf-del:hover { color: var(--red); background: var(--red-soft); }
@media (max-width: 480px) { .gf-form { grid-template-columns: 1fr; } }
</style>
