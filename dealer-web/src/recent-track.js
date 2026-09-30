// The stretch of road a truck is on now: its GPS points within 3 hours of
// the latest one (oldest -> newest), as [lat, lng] pairs.
export function recentTrack(points, hours = 3) {
  const pts = (points || []).filter((p) => p.latitude != null && p.longitude != null && p.received_at)
    .sort((a, b) => a.received_at.localeCompare(b.received_at))
  if (!pts.length) return []
  const cutoff = new Date(pts[pts.length - 1].received_at).getTime() - hours * 3600e3
  return pts.filter((p) => new Date(p.received_at).getTime() >= cutoff).map((p) => [p.latitude, p.longitude])
}
