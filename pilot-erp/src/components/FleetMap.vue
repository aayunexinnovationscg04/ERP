<template>
  <div class="map-wrap">
    <div ref="el" class="map"></div>
    <a v-if="googleMapsUrl" :href="googleMapsUrl" target="_blank" rel="noopener"
      class="gmaps-btn" title="Open in Google Maps">
      <ExternalLink :size="14" /> <span>Google Maps</span>
    </a>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from 'leaflet'
import { ExternalLink } from 'lucide-vue-next'
import { TILE_URL, TILE_ATTRIBUTION, TILE_SUBDOMAINS } from '../tiles'

const props = defineProps({
  markers: { type: Array, default: () => [] }, // [{id,lat,lng,label,status}]
  track: { type: Array, default: () => [] },    // [[lat,lng], ...]
})
const emit = defineEmits(['select'])

// Universal Google Maps link (opens the native app on phone, maps.google.com
// on desktop - same URL works for both, no device detection needed). Prefers
// the most recent track point (actual live GPS fix) over a marker's position,
// falling back to the first marker for maps with no route history.
const googleMapsUrl = computed(() => {
  const last = props.track.length ? props.track[props.track.length - 1] : null
  const [lat, lng] = last || (props.markers[0] ? [props.markers[0].lat, props.markers[0].lng] : [])
  if (lat == null || lng == null) return null
  return `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`
})

const el = ref(null)
let map, markerLayer, trackLayer

function draw() {
  if (!map) return
  markerLayer.clearLayers()
  trackLayer.clearLayers()
  const pts = []

  props.markers.forEach((m) => {
    if (m.lat == null || m.lng == null) return
    const icon = L.divIcon({
      className: 'live-marker', html: '<span class="live-dot"></span>',
      iconSize: [14, 14], iconAnchor: [7, 7],
    })
    const mk = L.marker([m.lat, m.lng], { icon })
      .bindTooltip(m.label || String(m.id), { permanent: false })
    mk.on('click', () => emit('select', m.id))
    mk.addTo(markerLayer)
    pts.push([m.lat, m.lng])
  })

  if (props.track.length > 1) {
    L.polyline(props.track, { color: '#3b82f6', weight: 4, opacity: 0.9, lineJoin: 'round' }).addTo(trackLayer)
    L.circleMarker(props.track[0], { radius: 6, color: '#22c55e', fillColor: '#22c55e', fillOpacity: 1 })
      .bindTooltip('Start').addTo(trackLayer)
    L.circleMarker(props.track[props.track.length - 1], { radius: 6, color: '#ef4444', fillColor: '#ef4444', fillOpacity: 1 })
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
})
onBeforeUnmount(() => map && map.remove())
watch(() => [props.markers, props.track], draw, { deep: true })
</script>
