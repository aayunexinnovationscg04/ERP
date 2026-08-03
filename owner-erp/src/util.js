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

// Builds an SVG-ready polyline/area from a list of numeric values. Returns
// null when there isn't enough data to draw a meaningful trend.
export function sparkline(values, { width = 300, height = 80, pad = 6 } = {}) {
  const s = values.filter((n) => Number.isFinite(n))
  if (s.length < 2) return null
  const base = height - pad
  const max = Math.max(...s, 1)
  const n = s.length
  const px = (i) => pad + (i / (n - 1)) * (width - pad * 2)
  const py = (val) => base - (val / max) * (height - pad * 2)
  const line = s.map((val, i) => `${px(i).toFixed(1)},${py(val).toFixed(1)}`).join(' ')
  const area = `${pad},${base} ${line} ${(width - pad).toFixed(1)},${base}`
  return { width, height, base, line, area }
}
