import axios from 'axios'
import { auth, setAuth, clearAuth } from './auth'

const api = axios.create({ baseURL: '/api' })

// Attach the access token.
api.interceptors.request.use((config) => {
  if (auth.access) config.headers.Authorization = `Bearer ${auth.access}`
  return config
})

// On 401, try one refresh, then replay; otherwise log out.
let refreshing = null
api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const { response, config } = error
    if (response?.status === 401 && auth.refresh && !config._retried) {
      config._retried = true
      try {
        refreshing = refreshing || axios.post('/api/auth/refresh', { refresh: auth.refresh })
        const { data } = await refreshing
        refreshing = null
        setAuth({ access: data.access })
        config.headers.Authorization = `Bearer ${data.access}`
        return api(config)
      } catch (e) {
        refreshing = null
        clearAuth()
        if (location.hash !== '#/login') location.hash = '#/login'
      }
    }
    return Promise.reject(error)
  },
)

export default api

// --- endpoint helpers (driver-scoped) ---
export const login = (username, password) =>
  api.post('/auth/login', { username, password }).then((r) => r.data)
export const getMe = () => api.get('/auth/me').then((r) => r.data)
export const getSummary = () => api.get('/driver/summary').then((r) => r.data)
export const getMyVehicle = () => api.get('/driver/vehicle').then((r) => r.data)
export const getMyTrack = (limit = 500) =>
  api.get('/driver/vehicle/telemetry', { params: { limit } }).then((r) => r.data)
export const getMyTrips = () => api.get('/driver/trips').then((r) => r.data)
export const getMyAlerts = (params = {}) =>
  api.get('/driver/alerts', { params }).then((r) => r.data)
