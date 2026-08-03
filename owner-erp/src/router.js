import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'

import Login from './views/Login.vue'
import Locations from './views/Locations.vue'
import Vehicles from './views/Vehicles.vue'
import VehicleDetail from './views/VehicleDetail.vue'
import FuelVehicles from './views/FuelVehicles.vue'
import FuelDetail from './views/FuelDetail.vue'
import Pilots from './views/Pilots.vue'
import PilotDetail from './views/PilotDetail.vue'
import Alerts from './views/Alerts.vue'
import Geofences from './views/Geofences.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', redirect: '/vehicles' }, // Vehicles is the default landing tab
  { path: '/locations', component: Locations },
  { path: '/vehicles', component: Vehicles },
  { path: '/vehicles/:id', component: VehicleDetail, props: true },
  { path: '/fuel', component: FuelVehicles },
  { path: '/fuel/:id', component: FuelDetail, props: true },
  { path: '/pilots', component: Pilots },
  { path: '/pilots/:id', component: PilotDetail, props: true },
  { path: '/alerts', component: Alerts },
  { path: '/geofences', component: Geofences },
]

const router = createRouter({ history: createWebHashHistory(), routes })

router.beforeEach((to) => {
  if (!to.meta.public && !auth.isAuthed) return '/login'
  if (to.path === '/login' && auth.isAuthed) return '/vehicles'
})

export default router
