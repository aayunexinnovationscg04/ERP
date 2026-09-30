import { createRouter, createWebHistory } from 'vue-router'
import { auth, sessionReady, setSessionEndHandler } from './auth'
import { canOpen, firstAllowedPath } from './access'

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
  { path: '/view-as', component: () => import('./views/ViewAs.vue'), meta: { public: true } },
  { path: '/', component: Home },
  { path: '/trips', component: Trips },
  { path: '/route-guidance', component: RouteGuidance },
  { path: '/alerts', component: Alerts },
  { path: '/navigation', component: Navigation },
  { path: '/profile', component: Profile },
]

// Old links used hash URLs (/pilot/#/users). Rewrite to the clean path before
// the router reads the location.
if (location.hash.startsWith('#/')) {
  history.replaceState(null, '', import.meta.env.BASE_URL + location.hash.slice(2))
}

const router = createRouter({ history: createWebHistory(import.meta.env.BASE_URL), routes })

router.beforeEach(async (to) => {
  await sessionReady  // restore the session from the refresh cookie before deciding
  if (!to.meta.public && !auth.isAuthed) {
    return { path: '/login', query: to.fullPath !== '/' ? { next: to.fullPath } : {} }
  }
  if (to.path === '/login' && auth.isAuthed) return '/'
  // Screens whose module is switched off for this account (Role Management).
  if (!to.meta.public && !canOpen(to.path)) return firstAllowedPath()
})

// Session revoked/expired mid-use (or signed out in another tab) -> back to login.
setSessionEndHandler(() => {
  const here = router.currentRoute.value
  if (!here.meta.public) router.replace({ path: '/login', query: { next: here.fullPath } })
})

export default router
