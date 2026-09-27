import axios from 'axios'
import { auth, ensureFreshToken, refreshSession } from './auth'

const api = axios.create({ baseURL: '/api' })

// Attach the in-memory access token (renewed first if it is about to expire).
api.interceptors.request.use(async (config) => {
  await ensureFreshToken()
  if (auth.access) config.headers.Authorization = `Bearer ${auth.access}`
  return config
})

// On 401, refresh once (shared across concurrent requests) and replay. If the
// session can't be renewed, auth.js ends it and the router shows the login.
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const { response, config } = error
    if (response?.status === 401 && config && !config._retried && auth.isAuthed) {
      config._retried = true
      if (await refreshSession()) {
        config.headers.Authorization = `Bearer ${auth.access}`
        return api(config)
      }
    }
    return Promise.reject(error)
  },
)

export default api

// List endpoints are limit/offset paginated (default 50); admin screens ask
// for a generous page so platform-wide lists aren't silently cut short.
const LIST_LIMIT = 500
const list = (url, params = {}) => api.get(url, { params: { limit: LIST_LIMIT, ...params } })
  .then((r) => r.data.results || r.data)
export const getCompanies = () => list('/admin/companies/')
export const createCompany = (body) => api.post('/admin/companies/', body).then((r) => r.data)
export const updateCompany = (id, body) => api.patch(`/admin/companies/${id}/`, body).then((r) => r.data)
export const getUsers = (params = {}) => list('/admin/users/', params)
export const createUser = (body) => api.post('/admin/users/', body).then((r) => r.data)
export const updateUser = (id, body) => api.patch(`/admin/users/${id}/`, body).then((r) => r.data)
// One-time ticket to open a user's portal in a new tab, view-only.
export const viewAsTicket = (id) => api.post(`/admin/users/${id}/view-as/`).then((r) => r.data)
export const getHealth = () => api.get('/admin/health').then((r) => r.data)
// cross-company fleet aggregate (Admin bypasses the company scoping this
// endpoint applies to dealers, so it returns platform-wide totals for us)
export const getFleetSummary = () => api.get('/dashboard/summary/').then((r) => r.data)
export const getDevices = () => list('/devices/')
export const getAlerts = (params = {}) => list('/alerts/', params)
