<template>
  <div ref="el" class="map"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from 'leaflet'
import { TILE_URL, TILE_ATTRIBUTION, TILE_SUBDOMAINS } from '../tiles'

const props = defineProps({
  markers: { type: Array, default: () => [] }, // [{id,lat,lng,label,status}]
  track: { type: Array, default: () => [] },    // [[lat,lng], ...]
})
const emit = defineEmits(['select'])

const el = ref(null)
let map, markerLayer, trackLayer

function draw() {
  if (!map) return
  markerLayer.clearLayers()
  trackLayer.clearLayers()
  const pts = []

  props.markers.forEach((m) => {
    if (m.lat == null || m.lng == null) return
    // live/latest position — pulsing brand marker
    const icon = L.divIcon({ className: '', html: '<div class="live-dot"></div>', iconSize: [16, 16], iconAnchor: [8, 8] })
    const tip = m.speed != null
      ? `${m.label || m.id} · ${m.speed} km/h`
      : (m.label || String(m.id))
    const mk = L.marker([m.lat, m.lng], { icon }).bindTooltip(tip, { permanent: false })
    mk.on('click', () => emit('select', m.id))
    mk.addTo(markerLayer)
    pts.push([m.lat, m.lng])
  })

  if (props.track.length > 1) {
    L.polyline(props.track, { color: '#ea580c', weight: 4, opacity: 0.85, lineJoin: 'round' }).addTo(trackLayer)
    L.circleMarker(props.track[0], { radius: 6, color: '#fff', weight: 2, fillColor: '#22c55e', fillOpacity: 1 })
      .bindTooltip('Start').addTo(trackLayer)
    L.circleMarker(props.track[props.track.length - 1], { radius: 6, color: '#fff', weight: 2, fillColor: '#ef4444', fillOpacity: 1 })
      .bindTooltip('Latest').addTo(trackLayer)
    props.track.forEach((p) => pts.push(p))
  }

  if (pts.length) map.fitBounds(L.latLngBounds(pts).pad(0.25), { maxZoom: 15 })
}

onMounted(() => {
  map = L.map(el.value, { zoomControl: true }).setView([21.145, 81.664], 12)
  L.tileLayer(TILE_URL, { subdomains: TILE_SUBDOMAINS, maxZoom: 20, attribution: TILE_ATTRIBUTION }).addTo(map)
  markerLayer = L.layerGroup().addTo(map)
  trackLayer = L.layerGroup().addTo(map)
  draw()
  // A map created inside a just-revealed container (e.g. an accordion panel)
  // can grab a stale width before layout settles — recompute once painted.
  requestAnimationFrame(() => map?.invalidateSize())
})
onBeforeUnmount(() => map && map.remove())
watch(() => [props.markers, props.track], draw, { deep: true })
</script>
