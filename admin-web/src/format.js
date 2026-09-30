// Display helpers shared by the admin views.
export const fmt = (n) => (n == null || n === '' ? '—' : Number(n).toLocaleString())

export function fmtDate(s) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })
}
export function fmtDateTime(s) {
  if (!s) return '—'
  return new Date(s).toLocaleString(undefined, { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}
export function fmtTime(d) {
  if (!d) return '—'
  return new Date(d).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })
}
export function relTime(s) {
  if (!s) return 'Never'
  const secs = Math.round((Date.now() - new Date(s).getTime()) / 1000)
  if (secs < 45) return 'Just now'
  const m = Math.round(secs / 60)
  if (m < 60) return `${m} min ago`
  const h = Math.round(m / 60)
  if (h < 24) return `${h} h ago`
  const d = Math.round(h / 24)
  if (d < 30) return `${d} d ago`
  return fmtDate(s)
}

// Turn a DRF error response into one readable sentence.
export function apiError(e, fallback = 'Something went wrong.') {
  const d = e?.response?.data
  if (!d) return e?.response ? fallback : 'Could not reach the server. Check your connection.'
  if (typeof d === 'string') return fallback
  if (d.detail) return d.detail
  const parts = Object.entries(d).map(([k, v]) => {
    const msg = Array.isArray(v) ? v.join(' ') : String(v)
    return k === 'non_field_errors' ? msg : `${k.replace(/_/g, ' ')}: ${msg}`
  })
  return parts.join(' ') || fallback
}

export const roleLabels = { admin: 'Admin', dealer: 'Dealer', manager: 'Manager', pilot: 'Pilot' }
export const roleLabel = (r) => roleLabels[r] || r || '—'
