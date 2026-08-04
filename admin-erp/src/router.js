import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'

// Route-level code-split (dynamic import) instead of static imports — see
// dealer-erp/src/router.js for why: statically importing every view meant
// Login couldn't render until the whole app's JS had downloaded, which reads
// as a hung/slow sign-in on a real mobile connection.
const Login = () => import('./views/Login.vue')
const Users = () => import('./views/Users.vue')
const Roles = () => import('./views/Roles.vue')
const UserPermissions = () => import('./views/UserPermissions.vue')
const Platform = () => import('./views/Platform.vue')
const Companies = () => import('./views/Companies.vue')
const CompanyAnalytics = () => import('./views/CompanyAnalytics.vue')
const FleetMonitoring = () => import('./views/FleetMonitoring.vue')
const Devices = () => import('./views/Devices.vue')
const PlatformLogs = () => import('./views/PlatformLogs.vue')
const SecurityAnalytics = () => import('./views/SecurityAnalytics.vue')
const Reports = () => import('./views/Reports.vue')

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', redirect: '/companies' }, // Companies: first item of the first sidebar group
  { path: '/companies', component: Companies },
  { path: '/company-analytics', component: CompanyAnalytics },
  { path: '/users', component: Users },
  { path: '/users/:id/permissions', component: UserPermissions, props: true },
  { path: '/roles', component: Roles },
  { path: '/fleet-monitoring', component: FleetMonitoring },
  { path: '/devices', component: Devices },
  { path: '/platform', component: Platform },
  { path: '/platform-logs', component: PlatformLogs },
  { path: '/security-analytics', component: SecurityAnalytics },
  { path: '/reports', component: Reports },
]

const router = createRouter({ history: createWebHashHistory(), routes })
router.beforeEach((to) => {
  if (!to.meta.public && !auth.isAuthed) return '/login'
  if (to.path === '/login' && auth.isAuthed) return '/'
})
export default router
