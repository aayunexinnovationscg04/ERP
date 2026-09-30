// One-click Google Maps links (open the Google Maps app on phones).
//
// With a recent route (>= 2 points) the link opens Google Maps directions
// from where the trip started, through points it passed, to where the truck
// is now — i.e. the road it is travelling. Otherwise it drops a pin on the
// truck's current position.
const ll = (p) => `${(+p[0]).toFixed(6)},${(+p[1]).toFixed(6)}`

export function googleMapsUrl(point, track = []) {
  const pts = (track || []).filter((p) => p && p[0] != null && p[1] != null)
  const here = point && point[0] != null && point[1] != null ? point : pts[pts.length - 1]
  if (!here) return null
  if (pts.length >= 2) {
    const origin = pts[0]
    const inner = pts.slice(1, -1)
    // Google allows up to 9 waypoints in a URL; sample evenly along the route
    const n = Math.min(8, inner.length)
    const way = Array.from({ length: n }, (_, i) => inner[Math.floor(((i + 1) * inner.length) / (n + 1))])
    const q = new URLSearchParams({ api: '1', origin: ll(origin), destination: ll(here), travelmode: 'driving' })
    if (way.length) q.set('waypoints', way.map(ll).join('|'))
    return `https://www.google.com/maps/dir/?${q.toString()}`
  }
  return `https://www.google.com/maps/search/?api=1&query=${ll(here)}`
}
