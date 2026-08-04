import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'

// Route-level code-split (dynamic import) instead of static imports — see
// dealer-erp/src/router.js for why: statically importing every view meant
// Login couldn't render until the whole app's JS had downloaded, which reads
// as a hung/slow sign-in on a real mobile connection. Home in particular
// pulls in the Leaflet map, so keeping it out of the initial bundle matters
// most here.
const Login = () => import('./views/Login.vue')
const Home = () => import('./views/Home.vue')
const Trips = () => import('./views/Trips.vue')
const Alerts = () => import('./views/Alerts.vue')
const RouteGuidance = () => import('./views/RouteGuidance.vue')
const Navigation = () => import('./views/Navigation.vue')
const Profile = () => import('./views/Profile.vue')

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
