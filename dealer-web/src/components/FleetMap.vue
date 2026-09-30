<!--
  Fleet map (Leaflet), used by every map in the portal.
  - Base map: OpenStreetMap, no key or account (tiles.js).
  - Trucks: status-coloured truck pins with a heading arrow (worked out from how
    the truck moved between refreshes); nearby trucks group into clusters.
  - Live: when positions refresh, pins glide to the new spot; "Follow" keeps the
    map on the focused truck.
  - One click "Google Maps" opens a new tab: the road the truck is travelling
    (trip start → points passed → now), or its current position (gmaps.js).
-->
<template>
  <div class="map-wrap">
    <div ref="el" class="map" :class="mapClass" :style="height ? { height } : null" role="region" :aria-label="ariaLabel"></div>
    <div v-if="emptyText && !hasPoints" class="map-empty"><span><MapPinOff :size="16" /> {{ emptyText }}</span></div>
    <div v-if="gmapsUrl || canFollow" class="map-tools">
      <button v-if="canFollow" type="button" class="map-tool" :class="{ on: following }" :aria-pressed="following"
              :title="following ? 'Stop following' : 'Keep the map on this truck'" @click="toggleFollow">
        <LocateFixed :size="15" /> <span>{{ following ? 'Following' : 'Follow' }}</span>
      </button>
      <a v-if="gmapsUrl" :href="gmapsUrl" target="_blank" rel="noopener" class="map-tool gmaps"
         :title="track.length > 1 ? 'Open the road this truck is travelling in Google Maps' : 'Open this position in Google Maps'">
        <Navigation2 :size="15" /> <span>Google Maps</span>
      </a>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import L from '../leaflet'
import { LocateFixed, MapPinOff, Navigation2 } from 'lucide-vue-next'
import { attachBaseMap } from '../tiles'
import { googleMapsUrl } from '../gmaps'

const props = defineProps({
  markers: { type: Array, default: () => [] }, // [{id,lat,lng,label,status,speed}]
  track: { type: Array, default: () => [] },    // [[lat,lng], ...]
  focus: { type: [String, Number], default: null }, // marker id to centre on
  endLabel: { type: String, default: 'Latest' },
  height: { type: String, default: '' },
  mapClass: { type: [String, Array, Object], default: '' },
  emptyText: { type: String, default: '' },
  cluster: { type: Boolean, default: true },     // group nearby trucks when there are many
  ariaLabel: { type: String, default: 'Map of vehicle positions' },
})
const emit = defineEmits(['select'])

// Leaflet needs literal colours: palette values from shared/design/tokens.css.
const C = { route: '#0284C7', start: '#059669', end: '#EA580C', ring: '#FFFFFF' }
const TRUCK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/></svg>'
const reduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches

const valid = (m) => m && m.lat != null && m.lng != null
const hasPoints = computed(() => props.markers.some(valid) || props.track.length > 0)
const focusMarker = computed(() => {
  if (props.focus != null) return props.markers.find((m) => m.id === props.focus && valid(m)) || null
  const vs = props.markers.filter(valid)
  return vs.length === 1 ? vs[0] : null
})
const gmapsUrl = computed(() => {
  const f = focusMarker.value
  if (f) return googleMapsUrl([f.lat, f.lng], props.track)
  return props.track.length ? googleMapsUrl(null, props.track) : null
})
const canFollow = computed(() => !!focusMarker.value)
const following = ref(false)

const el = ref(null)
let map, pinLayer, trackLayer, detachBase, ro
let lastFitKey = ''
const pins = new Map()   // id -> { marker, heading, anim }

// ---------- pins ----------
function pinHtml(m, heading, focused) {
  const arrow = heading == null ? '' : `<span class="fm-head" style="transform:rotate(${Math.round(heading)}deg)"></span>`
  return `<div class="fm-pin s-${m.status || 'unknown'}${focused ? ' focus' : ''}">${arrow}<span class="fm-body">${TRUCK_SVG}</span></div>`
}
function pinIcon(m, heading, focused) {
  const s = focused ? 40 : 32
  return L.divIcon({ className: 'fm-icon', html: pinHtml(m, heading, focused), iconSize: [s, s], iconAnchor: [s / 2, s / 2] })
}
function tip(m) { return m.speed != null && m.speed !== '' ? `${m.label || m.id} · ${m.speed} km/h` : (m.label || String(m.id)) }

// compass bearing a -> b in degrees
function bearing(a, b) {
  const r = Math.PI / 180
  const y = Math.sin((b.lng - a.lng) * r) * Math.cos(b.lat * r)
  const x = Math.cos(a.lat * r) * Math.sin(b.lat * r) - Math.sin(a.lat * r) * Math.cos(b.lat * r) * Math.cos((b.lng - a.lng) * r)
  return (Math.atan2(y, x) / r + 360) % 360
}

// glide a pin to its new position (1.2 s, eased); map follows if asked
function glide(p, to) {
  cancelAnimationFrame(p.anim)
  const from = p.marker.getLatLng()
  if (reduced || from.distanceTo(to) > 50000) { p.marker.setLatLng(to); follow(to); return }
  const t0 = performance.now(); const D = 1200
  const step = (t) => {
    if (!map) return
    const k = Math.min(1, (t - t0) / D); const e = k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2
    const pos = L.latLng(from.lat + (to.lat - from.lat) * e, from.lng + (to.lng - from.lng) * e)
    p.marker.setLatLng(pos); follow(pos)
    if (k < 1) p.anim = requestAnimationFrame(step)
  }
  p.anim = requestAnimationFrame(step)
}
function follow(pos) { if (map && following.value) map.panTo(pos, { animate: false }) }

function syncPins() {
  const focusId = focusMarker.value?.id
  const seen = new Set()
  props.markers.forEach((m) => {
    if (!valid(m)) return
    seen.add(m.id)
    const to = L.latLng(m.lat, m.lng)
    let p = pins.get(m.id)
    if (!p) {
      const marker = L.marker(to, { icon: pinIcon(m, null, m.id === focusId), zIndexOffset: m.id === focusId ? 1000 : 0, riseOnHover: true })
        .bindTooltip(tip(m), { direction: 'top', offset: [0, -16] })
      marker.on('click', () => emit('select', m.id))
      p = { marker, heading: null, anim: 0, key: '' }
      pins.set(m.id, p); pinLayer.addLayer(marker)
    } else {
      const from = p.marker.getLatLng()
      if (from.distanceTo(to) > 15) { p.heading = bearing(from, to); glide(p, to) }
      p.marker.setTooltipContent(tip(m))
    }
    const key = `${m.status}|${p.heading == null ? '' : Math.round(p.heading)}|${m.id === focusId}`
    if (key !== p.key) { p.key = key; p.marker.setIcon(pinIcon(m, p.heading, m.id === focusId)); p.marker.setZIndexOffset(m.id === focusId ? 1000 : 0) }
  })
  for (const [id, p] of pins) if (!seen.has(id)) { cancelAnimationFrame(p.anim); pinLayer.removeLayer(p.marker); pins.delete(id) }
}

function drawTrack() {
  trackLayer.clearLayers()
  if (props.track.length < 2) return
  L.polyline(props.track, { color: C.ring, weight: 8, opacity: 0.9, lineJoin: 'round', lineCap: 'round' }).addTo(trackLayer)
  L.polyline(props.track, { color: C.route, weight: 5, opacity: 1, lineJoin: 'round', lineCap: 'round' }).addTo(trackLayer)
  L.circleMarker(props.track[0], { radius: 7, color: C.ring, weight: 3, fillColor: C.start, fillOpacity: 1 }).bindTooltip('Start').addTo(trackLayer)
  if (!props.markers.some(valid)) {
    L.circleMarker(props.track[props.track.length - 1], { radius: 7, color: C.ring, weight: 3, fillColor: C.end, fillOpacity: 1 })
      .bindTooltip(props.endLabel).addTo(trackLayer)
  }
}

function fit() {
  const pts = [...props.markers.filter(valid).map((m) => [m.lat, m.lng]), ...props.track]
  // only re-fit when the set of things on the map changes (not on each refresh),
  // so the user's own pan/zoom isn't yanked back
  const key = props.markers.map((m) => m.id).join(',') + '|' + props.track.length + '|' + (props.track[0] || []).join(',')
  if (props.focus != null && focusMarker.value) return
  if (!pts.length || key === lastFitKey) return
  lastFitKey = key
  // programmatic moves never animate: an animation still running when the page
  // changes raised Leaflet's '_leaflet_pos' error
  if (pts.length === 1) map.setView(pts[0], 15, { animate: false })
  else map.fitBounds(L.latLngBounds(pts).pad(0.2), { maxZoom: 15, animate: false })
}

function draw() { if (!map) return; syncPins(); drawTrack(); fit() }

function centreOnFocus() {
  const f = props.focus != null ? focusMarker.value : null
  if (map && f) { map.setView([f.lat, f.lng], Math.max(map.getZoom(), 14), { animate: false }); pins.get(f.id)?.marker.openTooltip() }
}
function toggleFollow() {
  following.value = !following.value
  const f = focusMarker.value
  if (following.value && f && map) map.setView([f.lat, f.lng], Math.max(map.getZoom(), 15), { animate: false })
}

onMounted(() => {
  map = L.map(el.value, { zoomControl: true, worldCopyJump: true }).setView([21.145, 79.088], 12)
  detachBase = attachBaseMap(L, map)
  pinLayer = props.cluster && L.markerClusterGroup
    ? L.markerClusterGroup({
      showCoverageOnHover: false, maxClusterRadius: 48, spiderfyOnMaxZoom: true, disableClusteringAtZoom: 16,
      iconCreateFunction: (c) => L.divIcon({ className: 'fm-icon', html: `<div class="fm-cluster"><span>${c.getChildCount()}</span></div>`, iconSize: [40, 40] }),
    })
    : L.layerGroup()
  pinLayer.addTo(map)
  trackLayer = L.layerGroup().addTo(map)
  // stop following when the user drags the map themselves
  map.on('dragstart', () => { following.value = false })
  draw(); centreOnFocus()
  // a map inside a just-revealed or resized container needs its size re-read
  requestAnimationFrame(() => map?.invalidateSize())
  if ('ResizeObserver' in window) { ro = new ResizeObserver(() => map?.invalidateSize()); ro.observe(el.value) }
})
// stop animations and drop the reference, so a queued frame can't touch a removed map
onBeforeUnmount(() => {
  ro?.disconnect(); detachBase?.()
  for (const p of pins.values()) cancelAnimationFrame(p.anim)
  pins.clear()
  if (map) { map.stop(); map.off(); map.remove(); map = null }
})
watch(() => [props.markers, props.track], draw, { deep: true })
watch(() => props.focus, () => { following.value = false; draw(); centreOnFocus() })
defineExpose({ invalidate: () => map?.invalidateSize() })
</script>

<style>
/* marker + cluster styles (Leaflet puts these outside the component, so unscoped) */
.fm-icon { background: none; border: 0; }
.fm-pin { position: relative; width: 100%; height: 100%; }
.fm-body {
  position: absolute; inset: 3px; border-radius: 50%; display: grid; place-items: center;
  background: #64748B; color: #FFFFFF; border: 2.5px solid #FFFFFF; box-shadow: 0 2px 6px rgba(7, 21, 36, .35);
}
.fm-body svg { width: 58%; height: 58%; }
.fm-pin.s-active .fm-body { background: #059669; }
.fm-pin.s-idle .fm-body { background: #D97706; }
.fm-pin.s-offline .fm-body { background: #64748B; }
.fm-pin.s-maintenance .fm-body { background: #0B1F33; }
.fm-pin.focus .fm-body { background: #EA580C; }
/* heading arrow: a small wedge just outside the pin, rotated to the direction of travel */
.fm-head { position: absolute; inset: 0; pointer-events: none; }
.fm-head::before {
  content: ""; position: absolute; left: 50%; top: -5px; transform: translateX(-50%);
  border-left: 6px solid transparent; border-right: 6px solid transparent; border-bottom: 9px solid #0B1F33;
}
.fm-pin.focus .fm-head::before { border-bottom-color: #EA580C; }
.fm-cluster {
  width: 40px; height: 40px; border-radius: 50%; display: grid; place-items: center;
  background: #0B1F33; color: #FFFFFF; font: 800 13px/1 var(--font-ui); border: 3px solid #FFFFFF;
  box-shadow: 0 2px 8px rgba(7, 21, 36, .35);
}
.map-tools { position: absolute; top: 10px; right: 10px; z-index: 500; display: flex; gap: 8px; }
.map-tool {
  display: inline-flex; align-items: center; gap: 6px; height: 36px; padding: 0 12px; margin: 0;
  border-radius: var(--radius-sm); background: var(--surface); border: 1px solid var(--border-strong);
  color: var(--text); font: 700 12.5px/1 var(--font-ui); box-shadow: var(--shadow-md); cursor: pointer; transform: none;
}
.map-tool:hover { background: var(--surface-2); text-decoration: none; transform: none; }
.map-tool.on { background: var(--navy-900); border-color: var(--navy-900); color: #FFFFFF; }
.map-tool.gmaps { background: var(--brand); border-color: var(--brand); color: #FFFFFF; }
.map-tool.gmaps:hover { background: var(--brand-strong); }
.map-empty { position: absolute; inset: 0; z-index: 450; display: grid; place-items: center; pointer-events: none; }
.map-empty span {
  display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 999px;
  background: var(--surface); border: 1px solid var(--border); color: var(--muted); font-size: .8125rem; font-weight: 600;
}
@media (max-width: 720px) { .map-tool { height: 40px; } }
</style>
