import axios from 'axios'
import { auth, setAuth, clearAuth } from './auth'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((c) => {
  if (auth.access) c.headers.Authorization = `Bearer ${auth.access}`
  return c
})

let refreshing = null
api.interceptors.response.use((r) => r, async (error) => {
  const { response, config } = error
  if (response?.status === 401 && auth.refresh && !config._retried) {
    config._retried = true
    try {
      refreshing = refreshing || axios.post('/api/auth/refresh', { refresh: auth.refresh })
      const { data } = await refreshing; refreshing = null
      setAuth({ access: data.access })
      config.headers.Authorization = `Bearer ${data.access}`
      return api(config)
    } catch (e) { refreshing = null; clearAuth(); if (location.hash !== '#/login') location.hash = '#/login' }
  }
  return Promise.reject(error)
})

export default api

export const login = (u, p) => api.post('/auth/login', { username: u, password: p }).then((r) => r.data)
export const getModules = () => api.get('/admin/modules').then((r) => r.data)
export const getCompanies = () => api.get('/admin/companies/').then((r) => r.data.results || r.data)
export const getUsers = (params = {}) => api.get('/admin/users/', { params }).then((r) => r.data.results || r.data)
export const createUser = (body) => api.post('/admin/users/', body).then((r) => r.data)
export const updateUser = (id, body) => api.patch(`/admin/users/${id}/`, body).then((r) => r.data)
export const getUserPerms = (id) => api.get(`/admin/users/${id}/permissions/`).then((r) => r.data)
export const setUserPerms = (id, overrides) => api.put(`/admin/users/${id}/permissions/`, { overrides }).then((r) => r.data)
export const getRoles = () => api.get('/admin/roles').then((r) => r.data)
export const setRoles = (matrix) => api.put('/admin/roles', matrix).then((r) => r.data)
