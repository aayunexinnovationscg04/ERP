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

// --- endpoint helpers ---
export const login = (username, password) =>
  api.post('/auth/login', { username, password }).then((r) => r.data)
export const getMe = () => api.get('/auth/me').then((r) => r.data)
export const getVehicles = (params = {}) =>
  api.get('/vehicles/', { params }).then((r) => r.data.results || r.data)
export const getVehicle = (id) => api.get(`/vehicles/${id}/`).then((r) => r.data)
export const getVehicleTrack = (id, limit = 1000) =>
  api.get(`/vehicles/${id}/telemetry/`, { params: { limit } }).then((r) => r.data)
export const getVehicleTrips = (id) => api.get(`/vehicles/${id}/trips/`).then((r) => r.data)
export const getAlerts = (params = {}) =>
  api.get('/alerts/', { params }).then((r) => r.data.results || r.data)
export const ackAlert = (id) => api.post(`/alerts/${id}/acknowledge/`).then((r) => r.data)
export const sendCommand = (deviceId, payload) =>
  api.post(`/devices/${deviceId}/command/`, { payload }).then((r) => r.data)
export const setVehicleLocalName = (id, local_name) =>
  api.patch(`/vehicles/${id}/local_name/`, { local_name }).then((r) => r.data)
export const getDrivers = () => api.get('/drivers/').then((r) => r.data.results || r.data)
export const getDriver = (id) => api.get(`/drivers/${id}/`).then((r) => r.data)

// --- geofences ---
export const getGeofences = () =>
  api.get('/geofences/').then((r) => r.data.results || r.data)
export const createGeofence = (body) =>
  api.post('/geofences/', body).then((r) => r.data)
export const updateGeofence = (id, body) =>
  api.patch(`/geofences/${id}/`, body).then((r) => r.data)
export const deleteGeofence = (id) =>
  api.delete(`/geofences/${id}/`).then((r) => r.data)
