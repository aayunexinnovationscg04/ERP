// Small display helpers shared by the pilot views.

export function round1(n) { return Math.round((n || 0) * 10) / 10 }

export function timeOnly(s) {
  return s ? new Date(s).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' }) : '—'
}

export function dateTime(s) {
  if (!s) return '—'
  return new Date(s).toLocaleString([], { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' })
}

export function shortDate(s) {
  if (!s) return '—'
  return new Date(s).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' })
}

// "just now", "5 min ago", "3 h ago", "2 days ago", then a date.
export function timeAgo(s, now = Date.now()) {
  if (!s) return '—'
  const diff = Math.max(0, now - new Date(s).getTime())
  const m = Math.floor(diff / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m} min ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h} h ago`
  const d = Math.floor(h / 24)
  if (d < 7) return `${d} day${d > 1 ? 's' : ''} ago`
  return shortDate(s)
}

// "1 h 25 min" / "42 min" between two timestamps (end defaults to now).
export function duration(start, end) {
  if (!start) return '—'
  const ms = Math.max(0, (end ? new Date(end) : new Date()) - new Date(start))
  const mins = Math.round(ms / 60000)
  if (mins < 60) return `${mins} min`
  const h = Math.floor(mins / 60), m = mins % 60
  return m ? `${h} h ${m} min` : `${h} h`
}

// Today / Yesterday / "Fri, 25 Sep" for grouping lists by day.
export function dayLabel(s) {
  const d = new Date(s)
  const startOfDay = (x) => { const c = new Date(x); c.setHours(0, 0, 0, 0); return c.getTime() }
  const today = startOfDay(new Date())
  const day = startOfDay(d)
  if (day === today) return 'Today'
  if (day === today - 86400000) return 'Yesterday'
  return d.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' })
}
