// Base map for FleetMap.vue and Geofences.vue: the standard OpenStreetMap street
// map — free, no account, no API key (dimmed by CSS in dark mode). To look at a
// truck in Google Maps, the map's "Google Maps" button opens it in a new tab
// (gmaps.js), which needs no key either.
const OSM_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
const OSM_ATTR = '© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'

/** Put the base map on a Leaflet map. Returns a cleanup function. */
export function attachBaseMap(L, map) {
  const layer = L.tileLayer(OSM_URL, { maxZoom: 19, attribution: OSM_ATTR, className: 'osm-tiles' }).addTo(map)
  return () => { if (map.hasLayer(layer)) map.removeLayer(layer) }
}
