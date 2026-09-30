<template>
  <div class="map-wrap">
    <div ref="el" class="map" :class="mapClass" :style="height ? { height } : null"></div>
    <a v-if="googleMapsUrl" :href="googleMapsUrl" target="_blank" rel="noopener"
      class="map-overlay-btn" title="Open this position in Google Maps">
      <ExternalLink :size="14" /> <span class="hide-sm">Google Maps</span>
    </a>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from '../leaflet'
import { ExternalLink } from 'lucide-vue-next'
import { TILE_URL, TILE_ATTRIBUTION, TILE_SUBDOMAINS } from '../tiles'

const props = defineProps({
  markers: { type: Array, default: () => [] }, // [{id,lat,lng,label,status,speed}]
  track: { type: Array, default: () => [] },    // [[lat,lng], ...]
  focus: { type: [String, Number], default: null }, // marker id to centre on
  endLabel: { type: String, default: 'Latest' },
  height: { type: String, default: '' },
  mapClass: { type: [String, Array, Object], default: '' },
})
const emit = defineEmits(['select'])

// Universal Google Maps link (opens the native app on phones). Uses the
// focused marker, else the latest track point, else a lone marker.
const googleMapsUrl = computed(() => {
  let pt = null
  const f = props.focus != null ? props.markers.find((m) => m.id === props.focus) : null
  if (f) pt = [f.lat, f.lng]
  else if (props.track.length) pt = props.track[props.track.length - 1]
  else if (props.markers.length === 1) pt = [props.markers[0].lat, props.markers[0].lng]
  if (!pt || pt[0] == null || pt[1] == null) return null
  return `https://www.google.com/maps/search/?api=1&query=${pt[0]},${pt[1]}`
})

// Palette values from shared tokens (Leaflet needs literal colors).
const C = { route: '#0284C7', start: '#059669', end: '#EA580C', ring: '#FFFFFF' }

const el = ref(null)
let map, markerLayer, trackLayer
let lastFitKey = ''
const markerById = {}

function pinIcon(m, focused) {
  const s = m.status ? ` s-${m.status}` : ''
  const size = focused ? 22 : 16
  return L.divIcon({
    className: '', html: `<div class="veh-pin${s}${focused ? ' focus' : ''}"></div>`,
    iconSize: [size, size], iconAnchor: [size / 2, size / 2],
  })
}

function draw() {
  if (!map) return
  markerLayer.clearLayers()
  trackLayer.clearLayers()
  Object.keys(markerById).forEach((k) => delete markerById[k])
  const pts = []

  props.markers.forEach((m) => {
    if (m.lat == null || m.lng == null) return
    const focused = props.focus != null && m.id === props.focus
    const tip = m.speed != null ? `${m.label || m.id} · ${m.speed} km/h` : (m.label || String(m.id))
    const mk = L.marker([m.lat, m.lng], { icon: pinIcon(m, focused), zIndexOffset: focused ? 1000 : 0 })
      .bindTooltip(tip, { direction: 'top', offset: [0, -10] })
    mk.on('click', () => emit('select', m.id))
    mk.addTo(markerLayer)
    markerById[m.id] = mk
    pts.push([m.lat, m.lng])
  })

  if (props.track.length > 1) {
    L.polyline(props.track, { color: C.route, weight: 4, opacity: 0.9, lineJoin: 'round' }).addTo(trackLayer)
    L.circleMarker(props.track[0], { radius: 6, color: C.ring, weight: 2, fillColor: C.start, fillOpacity: 1 })
      .bindTooltip('Start').addTo(trackLayer)
    L.circleMarker(props.track[props.track.length - 1], { radius: 7, color: C.ring, weight: 2, fillColor: C.end, fillOpacity: 1 })
      .bindTooltip(props.endLabel).addTo(trackLayer)
    props.track.forEach((p) => pts.push(p))
  }

  // Only re-fit when the set of things on the map changes (not on every
  // 15s poll), so a user's own pan/zoom isn't yanked back each refresh.
  const fitKey = props.markers.map((m) => m.id).join(',') + '|' + props.track.length + '|' +
    (props.track[0] || []).join(',')
  const f = props.focus != null ? props.markers.find((m) => m.id === props.focus) : null
  if (f && f.lat != null) return
  if (pts.length && fitKey !== lastFitKey) {
    lastFitKey = fitKey
    if (pts.length === 1) map.setView(pts[0], 15)
    else map.fitBounds(L.latLngBounds(pts).pad(0.2), { maxZoom: 15 })
  }
}

function centreOnFocus() {
  const f = props.focus != null ? props.markers.find((m) => m.id === props.focus) : null
  if (map && f && f.lat != null) {
    map.setView([f.lat, f.lng], Math.max(map.getZoom(), 14))
    markerById[f.id]?.openTooltip()
  }
}

onMounted(() => {
  map = L.map(el.value, { zoomControl: true }).setView([21.145, 79.088], 12)
  L.tileLayer(TILE_URL, { subdomains: TILE_SUBDOMAINS, maxZoom: 20, attribution: TILE_ATTRIBUTION }).addTo(map)
  markerLayer = L.layerGroup().addTo(map)
  trackLayer = L.layerGroup().addTo(map)
  draw()
  centreOnFocus()
  // A map created inside a just-revealed container can grab a stale size.
  requestAnimationFrame(() => map?.invalidateSize())
})
// stop any pan/zoom animation first and drop the reference, so a queued frame
// can't touch a removed map (Leaflet '_leaflet_pos' error on fast page changes)
onBeforeUnmount(() => { if (map) { map.stop(); map.off(); map.remove(); map = null } })
watch(() => [props.markers, props.track], draw, { deep: true })
watch(() => props.focus, () => { draw(); centreOnFocus() })
defineExpose({ invalidate: () => map?.invalidateSize() })
</script>
