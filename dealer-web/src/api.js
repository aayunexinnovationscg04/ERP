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

// --- endpoint helpers ---
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
export const getPilots = () => api.get('/pilots/').then((r) => r.data.results || r.data)
export const getPilot = (id) => api.get(`/pilots/${id}/`).then((r) => r.data)

// --- geofences ---
export const getGeofences = () =>
  api.get('/geofences/').then((r) => r.data.results || r.data)
export const createGeofence = (body) =>
  api.post('/geofences/', body).then((r) => r.data)
export const updateGeofence = (id, body) =>
  api.patch(`/geofences/${id}/`, body).then((r) => r.data)
export const deleteGeofence = (id) =>
  api.delete(`/geofences/${id}/`).then((r) => r.data)
