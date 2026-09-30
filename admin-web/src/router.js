import { createRouter, createWebHistory } from 'vue-router'
import { auth, sessionReady, setSessionEndHandler } from './auth'

// Route-level code-split (dynamic import) instead of static imports — see
// dealer-web/src/router.js for why: statically importing every view meant
// Login couldn't render until the whole app's JS had downloaded, which reads
// as a hung/slow sign-in on a real mobile connection.
const Login = () => import('./views/Login.vue')
const Users = () => import('./views/Users.vue')
const Platform = () => import('./views/Platform.vue')
const Companies = () => import('./views/Companies.vue')
const CompanyAnalytics = () => import('./views/CompanyAnalytics.vue')
const FleetMonitoring = () => import('./views/FleetMonitoring.vue')
const Devices = () => import('./views/Devices.vue')
const DeviceData = () => import('./views/DeviceData.vue')
const PlatformLogs = () => import('./views/PlatformLogs.vue')
const SecurityAnalytics = () => import('./views/SecurityAnalytics.vue')
const Reports = () => import('./views/Reports.vue')

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', redirect: '/companies' }, // Companies: first item of the first sidebar group
  { path: '/:pathMatch(.*)*', redirect: '/' }, // removed or unknown pages (e.g. old /roles links)
  { path: '/companies', component: Companies },
  { path: '/company-analytics', component: CompanyAnalytics },
  { path: '/users', redirect: (to) => ({ path: '/dealers', query: to.query }) },
  { path: '/dealers', component: Users, props: { kind: 'dealer' } },
  { path: '/pilots', component: Users, props: { kind: 'pilot' } },
  { path: '/fleet-monitoring', component: FleetMonitoring },
  { path: '/devices', component: Devices },
  { path: '/device-data', component: DeviceData },
  { path: '/platform', component: Platform },
  { path: '/platform-logs', component: PlatformLogs },
  { path: '/security-analytics', component: SecurityAnalytics },
  { path: '/reports', component: Reports },
]

// Old links used hash URLs (/admin/#/users). Rewrite to the clean path before
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
})

// Session revoked/expired mid-use (or signed out in another tab) -> back to login.
setSessionEndHandler(() => {
  const here = router.currentRoute.value
  if (!here.meta.public) router.replace({ path: '/login', query: { next: here.fullPath } })
})

export default router
