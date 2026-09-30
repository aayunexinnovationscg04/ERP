// leaflet.markercluster expects a global `L`; this module runs before it is imported.
import L from 'leaflet'
window.L = L
export default L
