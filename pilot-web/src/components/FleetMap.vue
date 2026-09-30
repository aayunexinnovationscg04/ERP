<template>
  <div class="map-wrap">
    <div ref="el" class="map" :style="height ? { height } : null" role="region" aria-label="Map of your truck's location and route"></div>
    <div v-if="!hasPoints" class="map-empty"><span><MapPinOff :size="16" /> {{ emptyText }}</span></div>
    <a v-if="googleMapsUrl" :href="googleMapsUrl" target="_blank" rel="noopener"
      class="map-overlay-btn" title="Open this location in Google Maps">
      <ExternalLink :size="14" /> <span>Open in Maps</span>
    </a>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from '../leaflet'
import { ExternalLink, MapPinOff } from 'lucide-vue-next'
import { TILE_URL, TILE_ATTRIBUTION, TILE_SUBDOMAINS } from '../tiles'

const props = defineProps({
  markers: { type: Array, default: () => [] }, // [{id,lat,lng,label,status}]
  track: { type: Array, default: () => [] },    // [[lat,lng], ...]
  height: { type: String, default: '' },
  emptyText: { type: String, default: 'No GPS position yet' },
})
const emit = defineEmits(['select'])

// Leaflet draws on a canvas/SVG, so it needs literal colors — these are the
// palette values from shared/design/tokens.css.
const C = { route: '#0284C7', start: '#047857', latest: '#0B1F33', ring: '#FFFFFF' }
const TRUCK_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>'

const hasPoints = computed(() => props.markers.some((m) => m.lat != null && m.lng != null) || props.track.length > 0)

// Universal Google Maps link (opens the native app on phones). Prefers the
// latest track point, falling back to the first marker.
const googleMapsUrl = computed(() => {
  const last = props.track.length ? props.track[props.track.length - 1] : null
  const [lat, lng] = last || (props.markers[0] ? [props.markers[0].lat, props.markers[0].lng] : [])
  if (lat == null || lng == null) return null
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`
})

const el = ref(null)
let map, markerLayer, trackLayer, ro
let fitted = false // fit the view once; later 20s refreshes don't yank a map the pilot has panned

function draw() {
  if (!map) return
  markerLayer.clearLayers()
  trackLayer.clearLayers()
  const pts = []

  if (props.track.length > 1) {
    L.polyline(props.track, { color: C.route, weight: 5, opacity: 0.9, lineJoin: 'round', lineCap: 'round' }).addTo(trackLayer)
    L.circleMarker(props.track[0], { radius: 7, color: C.ring, weight: 3, fillColor: C.start, fillOpacity: 1 })
      .bindTooltip('Start of today\'s route').addTo(trackLayer)
    if (!props.markers.length) {
      L.circleMarker(props.track[props.track.length - 1], { radius: 7, color: C.ring, weight: 3, fillColor: C.latest, fillOpacity: 1 })
        .bindTooltip('Latest position').addTo(trackLayer)
    }
    props.track.forEach((p) => pts.push(p))
  }

  props.markers.forEach((m) => {
    if (m.lat == null || m.lng == null) return
    const icon = L.divIcon({
      className: 'truck-marker', html: `<span class="truck-pin">${TRUCK_SVG}</span>`,
      iconSize: [34, 34], iconAnchor: [17, 17],
    })
    const mk = L.marker([m.lat, m.lng], { icon, zIndexOffset: 1000 })
      .bindTooltip(m.label || String(m.id), { direction: 'top', offset: [0, -16] })
    mk.on('click', () => emit('select', m.id))
    mk.addTo(markerLayer)
    pts.push([m.lat, m.lng])
  })

  if (pts.length && !fitted) { map.fitBounds(L.latLngBounds(pts).pad(0.25), { maxZoom: 15, animate: false }); fitted = true }
}

onMounted(() => {
  map = L.map(el.value, { zoomControl: true, attributionControl: true }).setView([21.145, 81.664], 12)
  L.tileLayer(TILE_URL, { subdomains: TILE_SUBDOMAINS, maxZoom: 20, attribution: TILE_ATTRIBUTION }).addTo(map)
  markerLayer = L.layerGroup().addTo(map)
  trackLayer = L.layerGroup().addTo(map)
  draw()
  // keep tiles filling the box when the layout reflows (rail/sidebar toggle, rotation)
  if (typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver(() => map && map.invalidateSize())
    ro.observe(el.value)
  }
})
onBeforeUnmount(() => { ro && ro.disconnect(); if (map) { map.stop(); map.off(); map.remove(); map = null } })
watch(() => [props.markers, props.track], draw, { deep: true })
</script>
