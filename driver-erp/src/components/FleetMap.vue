<template>
  <div ref="el" class="map"></div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from 'leaflet'

const props = defineProps({
  markers: { type: Array, default: () => [] }, // [{id,lat,lng,label,status}]
  track: { type: Array, default: () => [] },    // [[lat,lng], ...]
})
const emit = defineEmits(['select'])

const el = ref(null)
let map, markerLayer, trackLayer

const COLOR = { active: '#22c55e', idle: '#f59e0b', offline: '#64748b', maintenance: '#94a3b8' }

function draw() {
  if (!map) return
  markerLayer.clearLayers()
  trackLayer.clearLayers()
  const pts = []

  props.markers.forEach((m) => {
    if (m.lat == null || m.lng == null) return
    const c = COLOR[m.status] || '#38bdf8'
    const mk = L.circleMarker([m.lat, m.lng], {
      radius: 9, color: '#0b1220', weight: 2, fillColor: c, fillOpacity: 1,
    }).bindTooltip(m.label || String(m.id), { permanent: false })
    mk.on('click', () => emit('select', m.id))
    mk.addTo(markerLayer)
    pts.push([m.lat, m.lng])
  })

  if (props.track.length > 1) {
    L.polyline(props.track, { color: '#38bdf8', weight: 3, opacity: 0.8 }).addTo(trackLayer)
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
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap', maxZoom: 19,
  }).addTo(map)
  markerLayer = L.layerGroup().addTo(map)
  trackLayer = L.layerGroup().addTo(map)
  draw()
})
onBeforeUnmount(() => map && map.remove())
watch(() => [props.markers, props.track], draw, { deep: true })
</script>
