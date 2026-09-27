import { auth } from './auth'

// Which Role Management module unlocks each screen (keys: backend core/modules.py).
// The API enforces the same modules; this only keeps the UI honest about it.
// Order matters: the first allowed screen is where a user lands.
const SCREENS = [
  ['/fleet-overview', 'dashboard'],
  ['/vehicles', 'fleet'],
  ['/vehicle-documents', 'fleet'],
  ['/locations', 'live_map'],
  ['/geofences', 'geofences'],
  ['/route-history', 'live_map'],
  ['/fuel', 'fuel'],
  ['/fuel-reports', 'fuel'],
  ['/fuel-efficiency', 'fuel'],
  ['/pilots', 'drivers'],
  ['/pilot-attendance', 'drivers'],
  ['/pilot-performance', 'drivers'],
  ['/pilot-salary', 'drivers'],
  ['/trip-planner', 'trips'],
  ['/trip-eta', 'trips'],
  ['/alerts', 'alerts'],
  ['/billing-orders', 'billing'],
  ['/billing-invoices', 'billing'],
  ['/billing-expenses', 'billing'],
  ['/ai-predictions', 'reports'],
  ['/ai-route-optimization', 'reports'],
]

function moduleFor(path) {
  const hit = SCREENS.find(([p]) => path === p || path.startsWith(p + '/'))
  return hit?.[1]
}

export function canOpen(path) {
  const m = moduleFor(path)
  const mods = auth.user?.modules
  return !m || !Array.isArray(mods) || mods.includes(m)
}

export function firstAllowedPath() {
  return SCREENS.find(([p]) => canOpen(p))?.[0] || '/no-access'
}
