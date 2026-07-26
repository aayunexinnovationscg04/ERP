import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'

import Login from './views/Login.vue'
import Dashboard from './views/Dashboard.vue'
import Fleet from './views/Fleet.vue'
import VehicleDetail from './views/VehicleDetail.vue'
import Alerts from './views/Alerts.vue'
import Geofences from './views/Geofences.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', component: Dashboard },
  { path: '/fleet', component: Fleet },
  { path: '/vehicles/:id', component: VehicleDetail, props: true },
  { path: '/alerts', component: Alerts },
  { path: '/geofences', component: Geofences },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to) => {
  if (!to.meta.public && !auth.isAuthed) return '/login'
  if (to.path === '/login' && auth.isAuthed) return '/'
})

export default router
