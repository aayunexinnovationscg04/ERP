import { reactive } from 'vue'

// Tiny reactive auth store persisted to localStorage.
const saved = JSON.parse(localStorage.getItem('fgx_auth') || '{}')

export const auth = reactive({
  access: saved.access || null,
  refresh: saved.refresh || null,
  user: saved.user || null,
  get isAuthed() { return !!this.access },
})

export function setAuth({ access, refresh, user }) {
  if (access !== undefined) auth.access = access
  if (refresh !== undefined) auth.refresh = refresh
  if (user !== undefined) auth.user = user
  localStorage.setItem('fgx_auth', JSON.stringify({
    access: auth.access, refresh: auth.refresh, user: auth.user,
  }))
}

export function clearAuth() {
  auth.access = auth.refresh = auth.user = null
  localStorage.removeItem('fgx_auth')
}
