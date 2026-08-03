import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'
import Login from './views/Login.vue'
import Home from './views/Home.vue'
import Trips from './views/Trips.vue'
import Alerts from './views/Alerts.vue'
import RouteGuidance from './views/RouteGuidance.vue'
import Navigation from './views/Navigation.vue'
import Profile from './views/Profile.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', component: Home },
  { path: '/trips', component: Trips },
  { path: '/route-guidance', component: RouteGuidance },
  { path: '/alerts', component: Alerts },
  { path: '/navigation', component: Navigation },
  { path: '/profile', component: Profile },
]

const router = createRouter({ history: createWebHashHistory(), routes })
router.beforeEach((to) => {
  if (!to.meta.public && !auth.isAuthed) return '/login'
  if (to.path === '/login' && auth.isAuthed) return '/'
})
export default router
