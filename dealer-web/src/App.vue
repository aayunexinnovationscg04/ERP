<template>
  <Toaster />
  <MotionConfig reduced-motion="user">
  <WelcomeGate v-if="justLoggedIn" :name="welcomeName" @done="justLoggedIn = false" />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <div class="scrim" :class="{ show: menuOpen }" @click="menuOpen = false" aria-hidden="true"></div>

    <aside class="sidebar" :class="{ open: menuOpen }" aria-label="Main navigation">
      <div class="sb-brand">
        <router-link :to="homePath" class="sb-home" title="Fuel Guard X">
          <span class="sb-logo"><img :src="logo" alt="AAYUNEX INNOVATIONS OPC Pvt Ltd. logo" /></span>
          <span class="sb-name"><strong>Fuel Guard X</strong><small>Dealer Portal</small></span>
        </router-link>
        <button type="button" class="sb-toggle" @click="collapsed = !collapsed"
                :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'" :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? PanelLeftOpen : PanelLeftClose" :size="17" />
        </button>
        <button type="button" class="sb-close" @click="menuOpen = false" aria-label="Close menu" title="Close menu">
          <X :size="20" />
        </button>
      </div>

      <nav class="sb-nav" @click="onNavClick">
        <section v-for="g in visibleGroups" :key="g.id" class="sb-sec">
          <h2 class="sb-sec-title">{{ g.label }}</h2>
          <router-link v-for="item in g.items" :key="item.to" :to="item.to"
            class="sb-link" :class="{ 'router-link-active': inSection(item.to) }"
            :title="collapsed ? item.label : undefined">
            <component :is="item.icon" :size="16" />
            <span class="label">{{ item.label }}</span>
            <span v-if="item.to === '/alerts' && openAlerts" class="nav-count">{{ openAlerts > 99 ? '99+' : openAlerts }}</span>
          </router-link>
        </section>
      </nav>

      <div class="sb-foot">
        <div class="sb-user" :title="collapsed ? userName : undefined">
          <span class="avatar">{{ initials }}</span>
          <span class="sb-user-text">
            <strong>{{ userName }}</strong>
            <small>{{ roleLabel }}{{ canWrite ? '' : ' · view only' }}</small>
          </span>
        </div>
        <button type="button" class="sb-icon-btn sb-logout" @click="logout" title="Log out" aria-label="Log out"><LogOut :size="17" /></button>
      </div>
    </aside>

    <div class="main-col">
      <header class="topbar">
        <button type="button" class="tb-btn tb-menu" aria-label="Open menu" :aria-expanded="menuOpen" @click="menuOpen = true">
          <Menu :size="22" />
        </button>
        <router-link v-if="crumb?.parentTo" :to="crumb.parentTo" class="tb-btn tb-back" :aria-label="`Back to ${crumb.group}`"><ArrowLeft :size="20" /></router-link>
        <nav class="crumbs" aria-label="Breadcrumb">
          <template v-if="crumb">
            <router-link v-if="crumb.parentTo" :to="crumb.parentTo" class="c-group c-link">{{ crumb.group }}</router-link>
            <span v-else class="c-group">{{ crumb.group }}</span>
            <ChevronRight class="c-sep" :size="14" />
            <span class="c-page">{{ crumb.page }}</span>
          </template>
          <span v-else class="c-page">Fuel Guard X</span>
        </nav>
        <div class="tb-spacer"></div>
        <div id="page-actions" class="tb-actions"></div>
        <div class="tb-right">
          <span v-if="!canWrite" class="ro-pill" title="Your account can view data but not change it.">
            <Eye :size="14" /><span>View only</span>
          </span>
          <router-link v-if="canOpen('/alerts')" to="/alerts" class="tb-btn tb-alerts" :title="openAlerts ? `${openAlerts} open alert(s)` : 'Alerts'"
                       :aria-label="openAlerts ? `${openAlerts} open alerts` : 'Alerts'">
            <Bell :size="18" />
            <span v-if="openAlerts" class="dotcount">{{ openAlerts > 99 ? '99+' : openAlerts }}</span>
          </router-link>
          <button type="button" class="tb-btn" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
                  :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
            <Sun v-if="theme === 'dark'" :size="18" />
            <Moon v-else :size="18" />
          </button>
        </div>
      </header>

      <main class="main">
        <div class="page">
          <div v-if="auth.viewOnly" class="view-banner" role="status">
            <Eye :size="16" aria-hidden="true" />
            <span>Viewing as <b>{{ auth.user.username }}</b> · view only<template v-if="auth.user.viewed_by"> · opened by {{ auth.user.viewed_by }}</template></span>
            <button type="button" class="view-close" @click="closeView">Close</button>
          </div>
          <div v-if="suspended" class="notice amber suspended-banner" role="status">
            <TriangleAlert :size="16" />
            <span><b>{{ companyName }} is suspended.</b> Live tracking and alerts may be paused. Contact your administrator to restore the account.</span>
          </div>
          <PageSkeleton v-if="showRouteSkeleton" />
          <router-view v-else v-slot="{ Component, route: r }">
            <div :key="r.fullPath" class="page-in"><component :is="Component" /></div>
          </router-view>
        </div>
      </main>
    </div>
  </div>
  </MotionConfig>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Menu, X, LocateFixed, Truck, Bell, MapPin, Fuel, IdCard, PanelLeftClose, PanelLeftOpen, LogOut, Sun, Moon, ChevronRight, Radar, History, BarChart3, TrendingUp, Users, CalendarCheck, Gauge, Wallet, Route, CalendarClock, Clock, ShieldAlert, ClipboardList, Receipt, Sparkles, BrainCircuit, Compass, FileText, LayoutDashboard, Eye, TriangleAlert } from 'lucide-vue-next'
import { MotionConfig } from 'motion-v'
import { auth, justLoggedIn, logout as endSession } from './auth'
import { getAlerts } from './api'
import { useTheme } from './theme'
import Toaster from './components/Toaster.vue'
import WelcomeGate from './components/WelcomeGate.vue'
import PageSkeleton from './components/PageSkeleton.vue'
import logo from '@shared/design/brand/aayunex-logo.png'
import { canOpen, firstAllowedPath } from './access'
import { pageMeta } from './pagemeta'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')

// Route-level chunks are lazy (see router.js). A slow chunk fetch gets a
// skeleton instead of a frozen page; the 150ms delay avoids a flash.
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

const welcomeName = computed(() => auth.user?.company?.name || auth.user?.username || 'Dealer')
const companyName = computed(() => auth.user?.company?.name || '')
const suspended = computed(() => { const st = auth.user?.company?.status; return !!st && st !== 'active' })
const canWrite = computed(() => auth.user?.may_write !== false)
const userName = computed(() => {
  const u = auth.user
  if (!u) return ''
  const full = [u.first_name, u.last_name].filter(Boolean).join(' ')
  return full || u.username
})
const initials = computed(() => {
  const parts = (userName.value || '?').replace(/[^A-Za-z0-9 ]/g, ' ').trim().split(/\s+/)
  return ((parts[0]?.[0] || '?') + (parts[1]?.[0] || '')).toUpperCase()
})
const roleLabel = computed(() => {
  const r = auth.user?.role || ''
  const nice = r ? r.charAt(0).toUpperCase() + r.slice(1) : 'User'
  return companyName.value ? `${nice} · ${companyName.value}` : nice
})

const menuOpen = ref(false)
const collapsed = ref(localStorage.getItem('fgx-sidebar-collapsed') === '1')
const { theme, toggleTheme } = useTheme()
watch(() => route.path, () => { menuOpen.value = false; window.scrollTo({ top: 0, left: 0 }); revealActiveLink() })
// The nav scrolls on short screens: keep the current page's link in view.
function revealActiveLink() {
  nextTick(() => document.querySelector('.sb-nav .sb-link.router-link-active')?.scrollIntoView({ block: 'nearest' }))
}
onMounted(revealActiveLink)
watch(menuOpen, (open) => { document.documentElement.classList.toggle('drawer-open', open) })
function onKey(e) { if (e.key === 'Escape' && menuOpen.value) menuOpen.value = false }
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
function onNavClick(e) { if (e.target.closest('a')) menuOpen.value = false }

// List routes and their /:id detail routes are flat siblings, so match the
// sidebar item by path prefix to keep it highlighted on detail pages.
function inSection(base) { return route.path === base || route.path.startsWith(base + '/') }
watch(collapsed, (v) => localStorage.setItem('fgx-sidebar-collapsed', v ? '1' : '0'))
async function logout() { await endSession(); router.push('/login') }

// Open-alert count for the bell + sidebar badge. Refreshed on navigation and
// every 60s; failures just hide the badge.
const openAlerts = ref(0)
let alertTimer = null
async function refreshAlertCount() {
  if (!auth.isAuthed || isLogin.value || !canOpen('/alerts')) return
  try {
    const list = await getAlerts({ status: 'open' })
    openAlerts.value = Array.isArray(list) ? list.length : 0
  } catch (e) { /* keep last value */ }
}
watch(() => route.path, refreshAlertCount, { immediate: true })
onMounted(() => { alertTimer = setInterval(refreshAlertCount, 60000) })
onBeforeUnmount(() => clearInterval(alertTimer))

// ---- grouped, collapsible sidebar nav ----
const NAV_GROUPS = [
  {
    id: 'fleet', label: 'Fleet', icon: Truck,
    items: [
      { to: '/fleet-overview', label: 'Fleet Overview', icon: LayoutDashboard },
      { to: '/vehicles', label: 'Vehicles', icon: Truck },
      { to: '/vehicle-documents', label: 'Vehicle Documents', icon: FileText },
    ],
  },
  {
    id: 'monitoring', label: 'Live Monitoring', icon: Radar,
    items: [
      { to: '/locations', label: 'Live Map', icon: LocateFixed },
      { to: '/geofences', label: 'Geofences', icon: MapPin },
      { to: '/route-history', label: 'Route History', icon: History },
    ],
  },
  {
    id: 'fuel', label: 'Fuel', icon: Fuel,
    items: [
      { to: '/fuel', label: 'Fuel Overview', icon: Fuel },
      { to: '/fuel-reports', label: 'Consumption Reports', icon: BarChart3 },
      { to: '/fuel-efficiency', label: 'Efficiency Analytics', icon: TrendingUp },
    ],
  },
  {
    id: 'drivers', label: 'Pilots', icon: Users,
    items: [
      { to: '/pilots', label: 'Pilots', icon: IdCard },
      { to: '/pilot-attendance', label: 'Attendance', icon: CalendarCheck },
      { to: '/pilot-performance', label: 'Performance', icon: Gauge },
      { to: '/pilot-salary', label: 'Salary', icon: Wallet },
    ],
  },
  {
    id: 'trips', label: 'Trips', icon: Route,
    items: [
      { to: '/trip-planner', label: 'Trip Planner', icon: CalendarClock },
      { to: '/trip-eta', label: 'ETA & Delivery', icon: Clock },
    ],
  },
  {
    id: 'alerts', label: 'Security', icon: ShieldAlert,
    items: [
      { to: '/alerts', label: 'Alerts', icon: Bell },
    ],
  },
  {
    id: 'billing', label: 'ERP & Billing', icon: Receipt,
    items: [
      { to: '/billing-orders', label: 'Order Booking', icon: ClipboardList },
      { to: '/billing-invoices', label: 'Challans & Invoices', icon: Receipt },
      { to: '/billing-expenses', label: 'Expenses', icon: Wallet },
    ],
  },
  {
    id: 'ai', label: 'AI Analytics', icon: Sparkles,
    items: [
      { to: '/ai-predictions', label: 'Predictions', icon: BrainCircuit },
      { to: '/ai-route-optimization', label: 'Route Optimization', icon: Compass },
    ],
  },
]

// Breadcrumb names the page (pages carry no big title of their own). Detail
// pages (/vehicles/:id) link back to their list and show the entity name.
const crumb = computed(() => {
  for (const g of NAV_GROUPS) {
    const item = g.items.find((i) => inSection(i.to))
    if (!item) continue
    if (route.path === item.to) return { group: g.label, page: item.label }
    return { group: item.label, parentTo: item.to, page: pageMeta.title || 'Details' }
  }
  if (route.path === '/no-access') return { group: 'Account', page: 'No access' }
  return null
})
const homePath = computed(() => (auth.user ? firstAllowedPath() : '/'))

// Only sections this account may open (Role Management modules).
const visibleGroups = computed(() => NAV_GROUPS
  .map((g) => ({ ...g, items: g.items.filter((i) => canOpen(i.to)) }))
  .filter((g) => g.items.length))

// view-as tab: closing it ends the read-only session
function closeView() { endSession() }
</script>
