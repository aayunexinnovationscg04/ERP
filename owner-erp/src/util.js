// Small formatting helpers shared across views.

export function fmt(n, dp = 1) {
  if (n === null || n === undefined) return '—'
  return Number(n).toFixed(dp)
}

export function ago(iso) {
  if (!iso) return 'never'
  const secs = (Date.now() - new Date(iso).getTime()) / 1000
  if (secs < 60) return `${Math.round(secs)}s ago`
  if (secs < 3600) return `${Math.round(secs / 60)}m ago`
  if (secs < 86400) return `${Math.round(secs / 3600)}h ago`
  return `${Math.round(secs / 86400)}d ago`
}

// green <3m, amber <15m, red older, gray if never seen.
export function freshness(vehicle) {
  const iso = vehicle.latest?.received_at
  if (!iso) return 'gray'
  const mins = (Date.now() - new Date(iso).getTime()) / 60000
  if (mins < 3) return 'green'
  if (mins < 15) return 'amber'
  return 'red'
}
