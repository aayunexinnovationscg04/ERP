import { auth } from './auth'

// Which Role Management module unlocks each screen (keys: backend core/modules.py).
// The API enforces the same modules; this only keeps the UI honest about it.
// Order matters: the first allowed screen is where a pilot lands.
const SCREENS = [
  ['/', 'driver_home'],
  ['/trips', 'driver_trips'],
  ['/route-guidance', 'driver_trips'],
  ['/navigation', 'driver_trips'],
  ['/alerts', 'driver_alerts'],
  ['/profile', null],
]

function moduleFor(path) {
  const hit = SCREENS.find(([p]) => path === p || (p !== '/' && path.startsWith(p + '/')))
  return hit?.[1]
}

export function canOpen(path) {
  const m = moduleFor(path)
  const mods = auth.user?.modules
  return !m || !Array.isArray(mods) || mods.includes(m)
}

export function firstAllowedPath() {
  return SCREENS.find(([p]) => canOpen(p))?.[0] || '/profile'
}
