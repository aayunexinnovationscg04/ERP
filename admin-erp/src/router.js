import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'
import Login from './views/Login.vue'
import Users from './views/Users.vue'
import Roles from './views/Roles.vue'
import UserPermissions from './views/UserPermissions.vue'
import Platform from './views/Platform.vue'
import Companies from './views/Companies.vue'
import CompanyAnalytics from './views/CompanyAnalytics.vue'
import FleetMonitoring from './views/FleetMonitoring.vue'
import Devices from './views/Devices.vue'
import PlatformLogs from './views/PlatformLogs.vue'
import SecurityAnalytics from './views/SecurityAnalytics.vue'
import Reports from './views/Reports.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', redirect: '/users' },
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
