import { reactive, ref } from 'vue'

const KEY = 'fgx_admin_auth'
const saved = JSON.parse(localStorage.getItem(KEY) || '{}')

export const auth = reactive({
  access: saved.access || null,
  refresh: saved.refresh || null,
  user: saved.user || null,
  get isAuthed() { return !!this.access },
  get isAdmin() { return this.user?.role === 'admin' },
})

// Set by Login.vue right after a successful sign-in; App.vue watches this to
// show the WelcomeGate overlay exactly once for that session.
export const justLoggedIn = ref(false)

export function setAuth({ access, refresh, user }) {
  if (access !== undefined) auth.access = access
  if (refresh !== undefined) auth.refresh = refresh
  if (user !== undefined) auth.user = user
  localStorage.setItem(KEY, JSON.stringify({ access: auth.access, refresh: auth.refresh, user: auth.user }))
}

export function clearAuth() {
  auth.access = auth.refresh = auth.user = null
  localStorage.removeItem(KEY)
}
