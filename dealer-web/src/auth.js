import axios from 'axios'
import { reactive, ref } from 'vue'

// Session store for the dealer portal.
//
// Security model (see backend core/tokens.py):
//  * The access token lives ONLY in memory here - never in localStorage - so a
//    page reload drops it and restoreSession() mints a fresh one.
//  * The refresh token is an HttpOnly cookie JS can never read; the server
//    rotates it on every refresh. Each portal has its own cookie, so the
//    admin, dealer and pilot sessions in one browser stay independent.
//  * Every auth call sends X-FGX-Portal; the server refuses accounts whose role
//    does not belong to this portal.
export const PORTAL = 'dealer'

// Tokens used to be persisted in localStorage; wipe any leftovers.
try { ['fgx_auth'].forEach((k) => localStorage.removeItem(k)) } catch (e) { /* storage blocked */ }

export const auth = reactive({
  access: null,
  user: null,
  get isAuthed() { return !!this.access },
  // Admin "view as" session: read-only, in memory only, never refreshed.
  get viewOnly() { return !!this.user?.view_only },
})

// Set by Login.vue right after a successful sign-in; App.vue watches this to
// show the WelcomeGate overlay exactly once for that session.
export const justLoggedIn = ref(false)

const http = axios.create({
  baseURL: '/api/auth',
  withCredentials: true,
  headers: { 'X-FGX-Portal': PORTAL },
})

// Other tabs of this portal: when one signs out, they all do.
const channel = typeof BroadcastChannel !== 'undefined' ? new BroadcastChannel(`fgx-session-${PORTAL}`) : null
channel?.addEventListener('message', (e) => { if (e.data === 'logout') endSession() })

// Non-secret hint that this browser holds a refresh cookie, so a signed-out
// visitor doesn't fire a pointless (401) refresh on every page load.
const HINT = `fgx_session_${PORTAL}`
const hint = {
  get: () => { try { return localStorage.getItem(HINT) === '1' } catch (e) { return true } },
  set: (on) => { try { on ? localStorage.setItem(HINT, '1') : localStorage.removeItem(HINT) } catch (e) { /* storage blocked */ } },
}

let onSessionEnd = () => {}
// The router registers how to get back to the login screen.
export function setSessionEndHandler(fn) { onSessionEnd = fn }

let refreshTimer = null
let expiresAt = 0
function apply(data) {
  hint.set(true)
  auth.access = data.access
  auth.user = data.user
  const ttl = data.access_expires_in || 600
  expiresAt = Date.now() + ttl * 1000
  clearTimeout(refreshTimer)
  // Renew a minute before expiry so normal use never hits a 401.
  refreshTimer = setTimeout(() => { refreshSession() }, Math.max(30, ttl - 60) * 1000)
}

// Timers don't run while a device sleeps or a background tab is throttled, so
// also renew just-in-time: before a request, and when the tab becomes visible.
export function ensureFreshToken() {
  if (auth.viewOnly) return Promise.resolve(Date.now() < expiresAt)
  if (auth.access && Date.now() > expiresAt - 15000) return refreshSession()
  return Promise.resolve(true)
}
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') ensureFreshToken()
})

export function clearAuth() {
  // A view-as tab must not touch the flag of a real session in this browser.
  if (!auth.viewOnly) hint.set(false)
  clearTimeout(refreshTimer)
  expiresAt = 0
  auth.access = null
  auth.user = null
}

function endSession() {
  const wasAuthed = auth.isAuthed
  clearAuth()
  if (wasAuthed) onSessionEnd()
}

export async function login(username, password) {
  const { data } = await http.post('/login', { username, password })
  apply(data)
  return data
}

// Admin "view as": the one-time ticket from the admin console becomes a short,
// read-only session for that user. Nothing is persisted (no cookie, no flag),
// so it ends with the tab and never touches anyone's real session.
export async function viewAs(ticket) {
  const { data } = await http.post('/view-as', { ticket })
  clearTimeout(refreshTimer)
  auth.access = data.access
  auth.user = data.user
  expiresAt = Date.now() + data.access_expires_in * 1000
  refreshTimer = setTimeout(() => endSession(), data.access_expires_in * 1000)
  return data
}

// Rotation makes a refresh token single-use, so concurrent refreshes (several
// 401s at once, or two tabs) must be serialised: one in-flight promise per tab,
// and a Web Lock across tabs so each tab sends the cookie the previous one set.
let inflight = null
export function refreshSession() {
  // Never swap a view-as session for whatever refresh cookie this browser holds.
  if (auth.viewOnly) { endSession(); return Promise.resolve(false) }
  if (inflight) return inflight
  const run = () => http.post('/refresh')
  const locked = navigator.locks?.request
    ? navigator.locks.request(`fgx-refresh-${PORTAL}`, run)
    : run()
  inflight = locked
    .then(({ data }) => { apply(data); return true })
    .catch((e) => {
      // 401/403 = session is gone. A network blip keeps the current state.
      if (!e.response || [401, 403].includes(e.response.status)) endSession()
      return false
    })
    .finally(() => { inflight = null })
  return inflight
}

// Called once at startup: turns the refresh cookie (if any) back into a session.
export const sessionReady = hint.get() ? refreshSession() : Promise.resolve(false)

export async function logout() {
  if (auth.viewOnly) { clearAuth(); window.close(); return }   // view-as tab: just close it
  try { await http.post('/logout') } catch (e) { /* cookie is cleared server-side anyway */ }
  clearAuth()
  channel?.postMessage('logout')
}

export async function logoutEverywhere() {
  try {
    await http.post('/logout-all', null, { headers: { Authorization: `Bearer ${auth.access}` } })
  } finally {
    clearAuth()
    channel?.postMessage('logout')
  }
}
