<template>
  <Toaster />
  <MotionConfig reduced-motion="user">
  <WelcomeGate v-if="justLoggedIn" :name="welcomeName" @done="justLoggedIn = false" />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <div class="scrim" :class="{ show: menuOpen }" @click="menuOpen = false" aria-hidden="true"></div>

    <aside class="sidebar" :class="{ open: menuOpen }" aria-label="Main navigation">
      <div class="side-head">
        <router-link to="/fleet-overview" class="brand" title="Fuel Guard X">
          <span class="logo-chip"><img :src="logo" alt="" /></span>
          <span class="brand-text"><span class="brand-title">Fuel Guard X</span><span class="brand-sub">Dealer Portal</span></span>
        </router-link>
        <button class="sb-icon-btn collapse-btn" @click="collapsed = !collapsed"
                :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'" :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? PanelLeftOpen : PanelLeftClose" :size="18" />
        </button>
        <button class="sb-icon-btn drawer-close" @click="menuOpen = false" aria-label="Close menu" title="Close menu">
          <X :size="20" />
        </button>
      </div>

      <nav class="nav" @click="onNavClick">
        <div class="nav-group" v-for="g in visibleGroups" :key="g.id">
          <button type="button" class="nav-group-head" :class="{ open: isGroupOpen(g), 'has-active': groupHasActiveRoute(g) }"
                  :aria-expanded="isGroupOpen(g)" @click.stop="toggleGroup(g.id)">
            <span class="gh-ic"><component :is="g.icon" :size="16" /></span>
            <span class="label">{{ g.label }}</span>
            <ChevronRight :size="15" class="chev" />
          </button>
          <div class="nav-group-items" :class="{ 'is-collapsed': !isGroupOpen(g) }">
            <router-link v-for="item in g.items" :key="item.to" :to="item.to" :title="item.label"
              class="nav-item" :class="{ 'router-link-active': inSection(item.to) }">
              <span class="ic"><component :is="item.icon" :size="17" /></span>
              <span class="label">{{ item.label }}</span>
              <span v-if="item.to === '/alerts' && openAlerts" class="nav-count">{{ openAlerts > 99 ? '99+' : openAlerts }}</span>
            </router-link>
          </div>
        </div>
      </nav>

      <div class="side-foot">
        <div class="side-user" :title="userName">
          <span class="avatar">{{ initials }}</span>
          <span class="side-user-text">
            <b>{{ userName }}</b>
            <small>{{ roleLabel }}{{ canWrite ? '' : ' · view only' }}</small>
          </span>
        </div>
        <div class="side-actions">
          <button class="side-btn logout" @click="logout" title="Log out">
            <LogOut :size="16" /><span class="label">Log out</span>
          </button>
        </div>
      </div>
    </aside>

    <div class="shell-main">
      <header class="appbar">
        <button class="hamburger" aria-label="Open menu" :aria-expanded="menuOpen" @click="menuOpen = true">
          <Menu :size="22" />
        </button>
        <router-link to="/fleet-overview" class="appbar-brand">
          <span class="logo-chip"><img :src="logo" alt="" /></span>
          <b>Fuel Guard X</b>
        </router-link>
        <div class="crumbs" v-if="crumb">
          <span class="crumb-group">{{ crumb.group }}</span>
          <ChevronRight :size="14" class="sep" />
          <b>{{ crumb.item }}</b>
        </div>
        <div class="appbar-right">
          <span v-if="!canWrite" class="ro-pill" title="Your account can view data but not change it.">
            <Eye :size="14" /><span>View only</span>
          </span>
          <span v-if="companyName" class="company-pill" :title="companyName">
            <Building2 :size="15" /><span>{{ companyName }}</span>
          </span>
          <router-link v-if="canOpen('/alerts')" to="/alerts" class="appbar-alerts icon-link" :title="openAlerts ? `${openAlerts} open alert(s)` : 'Alerts'"
                       :aria-label="openAlerts ? `${openAlerts} open alerts` : 'Alerts'">
            <Bell :size="18" />
            <span v-if="openAlerts" class="dotcount">{{ openAlerts > 99 ? '99+' : openAlerts }}</span>
          </router-link>
          <button class="icon-btn" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
                  :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
            <Sun v-if="theme === 'dark'" :size="18" />
            <Moon v-else :size="18" />
          </button>
        </div>
      </header>

      <main class="main">
        <div class="page">
          <div v-if="suspended" class="notice amber suspended-banner" role="status">
            <TriangleAlert :size="16" />
            <span><b>{{ companyName }} is suspended.</b> Live tracking and alerts may be paused. Contact your Aayunex administrator to restore the account.</span>
          </div>
          <PageSkeleton v-if="showRouteSkeleton" />
          <router-view v-else v-slot="{ Component, route: r }">
            <AnimatePresence mode="wait">
              <motion.div :key="r.fullPath"
                :initial="{ opacity: 0 }" :animate="{ opacity: 1 }" :exit="{ opacity: 0 }"
                :transition="{ duration: .14, ease: [.4, 0, .2, 1] }">
                <component :is="Component" />
              </motion.div>
            </AnimatePresence>
          </router-view>
        </div>
      </main>
    </div>
  </div>
  </MotionConfig>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Menu, X, LocateFixed, Truck, Bell, MapPin, Fuel, IdCard, PanelLeftClose, PanelLeftOpen, LogOut,
  Sun, Moon, ChevronRight, Radar, History, BarChart3, TrendingUp, Users, CalendarCheck, Gauge,
  Wallet, Route, CalendarClock, Clock, ShieldAlert, ClipboardList, Receipt, Sparkles, BrainCircuit,
  Compass, FileText, LayoutDashboard, Building2, Eye, TriangleAlert,
} from 'lucide-vue-next'
import { motion, AnimatePresence, MotionConfig } from 'motion-v'
import { auth, justLoggedIn, logout as endSession } from './auth'
import { getAlerts } from './api'
import { useTheme } from './theme'
import Toaster from './components/Toaster.vue'
import WelcomeGate from './components/WelcomeGate.vue'
import PageSkeleton from './components/PageSkeleton.vue'
import logo from '@shared/design/brand/fgx-mark.png'
import { canOpen } from './access'

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
watch(() => route.path, () => { menuOpen.value = false })
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

const crumb = computed(() => {
  for (const g of NAV_GROUPS) {
    const item = g.items.find((i) => inSection(i.to))
    if (item) return { group: g.label, item: item.label + (route.path !== item.to ? ' · Details' : '') }
  }
  return null
})

// Only sections this account may open (Role Management modules).
const visibleGroups = computed(() => NAV_GROUPS
  .map((g) => ({ ...g, items: g.items.filter((i) => canOpen(i.to)) }))
  .filter((g) => g.items.length))

const NAV_GROUPS_STORAGE_KEY = 'fgx_dealer_nav_groups'
function groupHasActiveRoute(g) { return g.items.some((item) => inSection(item.to)) }

// Accordion: one group open at a time so the sidebar stays short. Navigating
// into a section opens its group; clicking a header toggles it.
const initialGroup = NAV_GROUPS.find(groupHasActiveRoute)?.id
  ?? localStorage.getItem(NAV_GROUPS_STORAGE_KEY)
  ?? NAV_GROUPS[0].id
const openGroupId = ref(initialGroup)
watch(openGroupId, (v) => localStorage.setItem(NAV_GROUPS_STORAGE_KEY, v || ''))
watch(() => route.path, () => {
  const g = NAV_GROUPS.find(groupHasActiveRoute)
  if (g) openGroupId.value = g.id
})
function toggleGroup(id) { openGroupId.value = openGroupId.value === id ? null : id }
function isGroupOpen(g) { return openGroupId.value === g.id }
</script>
