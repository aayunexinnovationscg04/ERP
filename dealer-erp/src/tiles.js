// Map tile source, shared by FleetMap.vue and Geofences.vue.
// Plain OpenStreetMap standard tiles: the map data is free (ODbL license),
// no API key, no billing account, no card. Their tile server does ask
// production apps not to hammer it at high volume (see the OSM Tile Usage
// Policy) — fine at this fleet's scale; if traffic ever grows a lot, move to
// a paid/dedicated OSM-tile host rather than switching data providers.
export const TILE_URL = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
export const TILE_ATTRIBUTION =
  '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
export const TILE_SUBDOMAINS = ''
