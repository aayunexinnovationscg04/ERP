import { createRouter, createWebHashHistory } from 'vue-router'
import { auth } from './auth'
import Login from './views/Login.vue'
import Users from './views/Users.vue'
import Roles from './views/Roles.vue'
import UserPermissions from './views/UserPermissions.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', redirect: '/users' },
  { path: '/users', component: Users },
  { path: '/users/:id/permissions', component: UserPermissions, props: true },
  { path: '/roles', component: Roles },
]

const router = createRouter({ history: createWebHashHistory(), routes })
router.beforeEach((to) => {
  if (!to.meta.public && !auth.isAuthed) return '/login'
  if (to.path === '/login' && auth.isAuthed) return '/'
})
export default router
