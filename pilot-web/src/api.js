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

// --- endpoint helpers (pilot-scoped) ---
export const getMe = () => api.get('/auth/me').then((r) => r.data)
export const getSummary = () => api.get('/pilot/summary').then((r) => r.data)
export const getMyVehicle = () => api.get('/pilot/vehicle').then((r) => r.data)
export const getMyTrack = (limit = 500) =>
  api.get('/pilot/vehicle/telemetry', { params: { limit } }).then((r) => r.data)
export const getMyTrips = () => api.get('/pilot/trips').then((r) => r.data)
export const getMyAlerts = (params = {}) =>
  api.get('/pilot/alerts', { params }).then((r) => r.data)
