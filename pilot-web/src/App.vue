<template>
  <Toaster />
  <WelcomeGate v-if="justLoggedIn" :name="welcomeName" @done="justLoggedIn = false" />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <!-- phone: fixed top bar (brand + theme + sign out). Primary nav lives in
         the thumb-reachable bottom tab bar. -->
    <header class="topbar">
      <div class="brand-lockup">
        <span class="logo-tile"><img :src="logo" alt="" /></span>
        <span class="brand-text">
          <span class="brand-sub">AAYUNEX INNOVATIONS OPC Pvt Ltd.</span>
          <span class="brand-name">Fuel Guard X</span>
        </span>
      </div>
      <span class="spacer"></span>
      <button class="icon-btn" type="button" @click="toggleTheme"
        :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
        :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
        <Sun v-if="theme === 'dark'" :size="20" :stroke-width="2.25" />
        <Moon v-else :size="20" :stroke-width="2.25" />
      </button>
      <button class="icon-btn" type="button" @click="logout" aria-label="Log out" title="Log out">
        <LogOut :size="20" :stroke-width="2.25" />
      </button>
    </header>

    <!-- tablet: icon rail · desktop: full sidebar (collapsible to the rail) -->
    <aside class="sidebar" aria-label="Main navigation">
      <div class="side-head">
        <div class="brand-lockup">
          <span class="logo-tile"><img :src="logo" alt="" /></span>
          <span class="brand-text">
            <span class="brand-sub">Pilot App</span>
            <span class="brand-name">Fuel Guard X</span>
          </span>
        </div>
        <button class="icon-btn collapse-btn" type="button" @click="collapsed = !collapsed"
          :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? ChevronsRight : ChevronsLeft" :size="18" :stroke-width="2.25" />
        </button>
      </div>

      <nav class="side-nav">
        <template v-for="g in visibleNavGroups" :key="g.label">
          <div class="side-section">{{ g.label }}</div>
          <router-link v-for="item in g.items" :key="item.to" :to="item.to" class="side-link" :title="item.label">
            <component :is="item.icon" :size="20" :stroke-width="2.25" />
            <span>{{ item.short || item.label }}</span>
            <span v-if="item.to === '/alerts' && openAlerts" class="count" :aria-label="`${openAlerts} open alerts`">{{ openAlerts > 99 ? '99+' : openAlerts }}</span>
          </router-link>
        </template>
      </nav>

      <div class="side-foot">
        <div class="side-user" :title="auth.user?.username">
          <span class="avatar">{{ initials }}</span>
          <span class="side-user-text">
            <strong>{{ auth.user?.username || 'Pilot' }}</strong>
            <small>{{ auth.user?.company?.name || 'Pilot' }}</small>
          </span>
        </div>
        <button class="side-btn" type="button" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
          <Sun v-if="theme === 'dark'" :size="18" :stroke-width="2.25" />
          <Moon v-else :size="18" :stroke-width="2.25" />
          <span class="label">{{ theme === 'dark' ? 'Light mode' : 'Dark mode' }}</span>
        </button>
        <button class="side-btn logout" type="button" @click="logout" title="Log out">
          <LogOut :size="18" :stroke-width="2.25" /><span class="label">Log out</span>
        </button>
      </div>
    </aside>

    <main class="main">
      <div class="page">
        <div v-if="auth.viewOnly" class="view-banner" role="status">
          <Eye :size="16" aria-hidden="true" />
          <span>Viewing as <b>{{ auth.user.username }}</b> · view only<template v-if="auth.user.viewed_by"> · opened by {{ auth.user.viewed_by }}</template></span>
          <button type="button" class="view-close" @click="closeView">Close</button>
        </div>
        <PageSkeleton v-if="showRouteSkeleton" />
        <AnimatePresence v-else mode="wait">
          <motion.div :key="$route.fullPath"
            :initial="{ opacity: 0, y: reduced ? 0 : 6 }"
            :animate="{ opacity: 1, y: 0 }"
            :exit="{ opacity: 0 }"
            :transition="pageTransition(reduced)">
            <router-view v-slot="{ Component }">
              <component :is="Component" />
            </router-view>
          </motion.div>
        </AnimatePresence>
      </div>
    </main>

    <!-- phone bottom tab bar: five primary destinations. Route Guidance is
         reached from the active trip on the Trips page. -->
    <nav class="tabbar" aria-label="Main navigation">
      <router-link v-for="t in visibleTabs" :key="t.to" :to="t.to" class="tab" :aria-label="t.label">
        <span class="tab-ic">
          <component :is="t.icon" :size="22" :stroke-width="2.25" />
          <span v-if="t.to === '/alerts' && openAlerts" class="tab-badge">{{ openAlerts > 9 ? '9+' : openAlerts }}</span>
        </span>
        <span class="tab-label">{{ t.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { motion, AnimatePresence } from 'motion-v'
import { Truck, Route, ChevronsLeft, ChevronsRight, LogOut, Sun, Moon, User, ShieldAlert, Compass, Navigation, Eye } from 'lucide-vue-next'
import Toaster from './components/Toaster.vue'
import WelcomeGate from './components/WelcomeGate.vue'
import PageSkeleton from './components/PageSkeleton.vue'
import { auth, justLoggedIn, logout as endSession } from './auth'
import { getSummary } from './api'
import { usePrefersReducedMotion, pageTransition } from './motion'
import { useTheme } from './theme'
import logo from '@shared/design/brand/aayunex-logo.png'
import { canOpen } from './access'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const welcomeName = computed(() => {
  const u = auth.user?.username
  return u ? u.charAt(0).toUpperCase() + u.slice(1) : 'Pilot'
})
const initials = computed(() => (auth.user?.username || 'P').charAt(0).toUpperCase())
const collapsed = ref(localStorage.getItem('fgx-pilot-sidebar-collapsed') === '1')
watch(collapsed, (v) => localStorage.setItem('fgx-pilot-sidebar-collapsed', v ? '1' : '0'))
const reduced = usePrefersReducedMotion()
const { theme, toggleTheme } = useTheme()

const navGroups = [
  { label: 'Vehicle', items: [{ to: '/', label: 'My Truck', icon: Truck }] },
  {
    label: 'Trip operations',
    items: [
      { to: '/trips', label: 'Trips', icon: Route },
      { to: '/route-guidance', label: 'Route Guidance', short: 'Guidance', icon: Navigation },
      { to: '/navigation', label: 'Traffic & Delays', short: 'Traffic', icon: Compass },
    ],
  },
  { label: 'Safety', items: [{ to: '/alerts', label: 'Alerts', icon: ShieldAlert }] },
  { label: 'Account', items: [{ to: '/profile', label: 'Profile', icon: User }] },
]
const tabs = [
  { to: '/', label: 'My Truck', icon: Truck },
  { to: '/trips', label: 'Trips', icon: Route },
  { to: '/navigation', label: 'Traffic', icon: Compass },
  { to: '/alerts', label: 'Alerts', icon: ShieldAlert },
  { to: '/profile', label: 'Profile', icon: User },
]
// Only screens this pilot may open (Role Management modules).
const visibleNavGroups = computed(() => navGroups
  .map((g) => ({ ...g, items: g.items.filter((i) => canOpen(i.to)) }))
  .filter((g) => g.items.length))
const visibleTabs = computed(() => tabs.filter((t) => canOpen(t.to)))

// Open-alert count for the Alerts tab/nav badge (same /pilot/summary the
// home page reads), refreshed on every navigation.
const openAlerts = ref(0)
async function refreshCount() {
  if (!auth.isAuthed || isLogin.value) return
  try { openAlerts.value = (await getSummary()).open_alerts || 0 } catch (e) { /* keep last */ }
}
watch([() => route.path, () => auth.isAuthed], () => { refreshCount() }, { immediate: true })

// The phone layout scrolls the document; start each page at the top.
watch(() => route.path, () => { if (typeof window !== 'undefined') window.scrollTo(0, 0) })

// Route chunks are lazy (see router.js). A slow first fetch shows a skeleton
// after 150ms instead of a frozen page.
const showRouteSkeleton = ref(false)
let skeletonShowTimer = null
router.beforeEach((to) => {
  if (to.meta.public) return
  clearTimeout(skeletonShowTimer)
  skeletonShowTimer = setTimeout(() => { showRouteSkeleton.value = true }, 150)
})
router.afterEach(() => {
  clearTimeout(skeletonShowTimer)
  showRouteSkeleton.value = false
})

async function logout() { openAlerts.value = 0; await endSession(); router.push('/login') }

// view-as tab: closing it ends the read-only session
function closeView() { endSession() }
</script>
