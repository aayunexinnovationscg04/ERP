<template>
  <Toaster />
  <MotionConfig reduced-motion="user">
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <div class="mobilebar">
      <motion.button class="hamburger" aria-label="Menu" :while-tap="{ scale: .88 }" @click="menuOpen = !menuOpen">
        <AnimatePresence mode="wait">
          <motion.span :key="menuOpen ? 'x' : 'menu'" class="hamburger-ic"
            :initial="{ opacity: 0, rotate: -90 }" :animate="{ opacity: 1, rotate: 0 }" :exit="{ opacity: 0, rotate: 90 }"
            :transition="{ duration: .16, ease: [.4, 0, .2, 1] }">
            <component :is="menuOpen ? X : Menu" :size="22" />
          </motion.span>
        </AnimatePresence>
      </motion.button>
      <div class="mb-brand"><span class="logo-chip"><img :src="logo" alt="" /></span> <span>Fuel Guard X</span></div>
      <div class="spacer"></div>
      <button class="theme-toggle mb-theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
        <Sun v-if="theme === 'dark'" :size="18" />
        <Moon v-else :size="18" />
      </button>
    </div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="side-head">
        <div class="brand side-brand"><span class="logo-chip"><img :src="logo" alt="" class="side-brand-logo" /></span> <span class="label">Fuel Guard X</span></div>
        <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
          <Sun v-if="theme === 'dark'" :size="16" />
          <Moon v-else :size="16" />
        </button>
        <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? ChevronsRight : ChevronsLeft" :size="16" />
        </button>
      </div>
      <nav class="nav" @click="menuOpen = false">
        <div class="nav-group" v-for="g in NAV_GROUPS" :key="g.id">
          <button type="button" class="nav-group-head" :class="{ open: isGroupOpen(g) }" @click.stop="toggleGroup(g.id)">
            <span class="ic" :class="g.hue"><component :is="g.icon" :size="14" /></span>
            <span class="label">{{ g.label }}</span>
            <ChevronRight :size="14" class="chev" />
          </button>
          <div class="nav-group-items" :class="{ 'is-collapsed': !isGroupOpen(g) }">
            <router-link v-for="item in g.items" :key="item.to" :to="item.to" :title="item.label"
              class="nav-item" :class="[g.hue, { 'router-link-active': inSection(item.to) }]">
              <span class="ic"><component :is="item.icon" :size="17" /></span>
              <span class="label">{{ item.label }}</span>
            </router-link>
          </div>
        </div>
      </nav>
      <div class="spacer" style="flex:1"></div>
      <button class="logout-btn" style="margin-top:12px" @click="logout" title="Log out">
        <PowerOff :size="16" class="ic" /><span class="label">Log out</span>
      </button>
    </aside>
    <main class="main">
      <router-view v-slot="{ Component, route: r }">
        <AnimatePresence mode="wait">
          <motion.div :key="r.fullPath"
            :initial="{ opacity: 0, y: 8 }" :animate="{ opacity: 1, y: 0 }" :exit="{ opacity: 0, y: -6 }"
            :transition="{ duration: .22, ease: [.4, 0, .2, 1] }">
            <component :is="Component" />
          </motion.div>
        </AnimatePresence>
      </router-view>
    </main>
  </div>
  </MotionConfig>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Menu, X, LocateFixed, Truck, Bell, MapPin, Fuel, IdCard, ChevronsLeft, ChevronsRight, PowerOff,
  Sun, Moon, ChevronRight, Radar, History, BarChart3, TrendingUp, Users, CalendarCheck, Gauge,
  Wallet, Route, CalendarClock, Clock, ShieldAlert, ClipboardList, Receipt, Sparkles, BrainCircuit,
  Compass, FileText,
} from 'lucide-vue-next'
import { motion, AnimatePresence, MotionConfig } from 'motion-v'
import { auth, clearAuth } from './auth'
import { useTheme } from './theme'
import Toaster from './components/Toaster.vue'
import logo from './assets/logo.png'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
const collapsed = ref(localStorage.getItem('fgx-sidebar-collapsed') === '1')
const { theme, toggleTheme } = useTheme()
watch(() => route.path, () => { menuOpen.value = false })
// The list routes and their /:id detail routes are flat siblings, not nested
// children, so vue-router's own router-link-active (matched-record based) drops
// once you're on e.g. /vehicles/123. Match by path prefix instead so the sidebar
// item stays highlighted while inside that section's detail pages.
function inSection(base) { return route.path === base || route.path.startsWith(base + '/') }
watch(collapsed, (v) => localStorage.setItem('fgx-sidebar-collapsed', v ? '1' : '0'))
function logout() { clearAuth(); router.push('/login') }

// ---- grouped, collapsible sidebar nav ----
// Each group owns one jewel-tone hue (shared by every item's icon chip inside
// it, same convention the old flat nav used per-section), a Lucide icon for
// its collapsible header, and its member routes.
const NAV_GROUPS = [
  {
    id: 'fleet', label: 'Fleet Management', icon: Truck, hue: 'blue',
    items: [
      { to: '/fleet-overview', label: 'Fleet Overview', icon: Gauge },
      { to: '/vehicles', label: 'Vehicles', icon: Truck },
      { to: '/vehicle-documents', label: 'Vehicle Documents', icon: FileText },
    ],
  },
  {
    id: 'monitoring', label: 'Live Monitoring', icon: Radar, hue: 'cyan',
    items: [
      { to: '/locations', label: 'Live Map', icon: LocateFixed },
      { to: '/geofences', label: 'Geofences', icon: MapPin },
      { to: '/route-history', label: 'Route History', icon: History },
    ],
  },
  {
    id: 'fuel', label: 'Fuel Monitoring', icon: Fuel, hue: 'violet',
    items: [
      { to: '/fuel', label: 'Fuel Overview', icon: Fuel },
      { to: '/fuel-reports', label: 'Consumption Reports', icon: BarChart3 },
      { to: '/fuel-efficiency', label: 'Efficiency Analytics', icon: TrendingUp },
    ],
  },
  {
    id: 'drivers', label: 'Driver Management', icon: Users, hue: 'teal',
    items: [
      { to: '/pilots', label: 'Pilots', icon: IdCard },
      { to: '/pilot-attendance', label: 'Attendance', icon: CalendarCheck },
      { to: '/pilot-performance', label: 'Performance & Behavior', icon: Gauge },
      { to: '/pilot-salary', label: 'Salary', icon: Wallet },
    ],
  },
  {
    id: 'trips', label: 'Trip Management', icon: Route, hue: 'green',
    items: [
      { to: '/trip-planner', label: 'Trip Planner', icon: CalendarClock },
      { to: '/trip-eta', label: 'ETA & Delivery', icon: Clock },
    ],
  },
  {
    id: 'alerts', label: 'Alerts & Security', icon: ShieldAlert, hue: 'crit',
    items: [
      { to: '/alerts', label: 'Alerts', icon: Bell },
    ],
  },
  {
    id: 'billing', label: 'ERP & Billing', icon: Receipt, hue: 'amber',
    items: [
      { to: '/billing-orders', label: 'Order Booking', icon: ClipboardList },
      { to: '/billing-invoices', label: 'Challans & Invoices', icon: Receipt },
      { to: '/billing-expenses', label: 'Expense Tracking', icon: Wallet },
    ],
  },
  {
    id: 'ai', label: 'AI Analytics', icon: Sparkles, hue: 'gray',
    items: [
      { to: '/ai-predictions', label: 'Predictions', icon: BrainCircuit },
      { to: '/ai-route-optimization', label: 'Route Optimization', icon: Compass },
    ],
  },
]

const NAV_GROUPS_STORAGE_KEY = 'fgx_dealer_nav_groups'
function loadGroupState() {
  try { return JSON.parse(localStorage.getItem(NAV_GROUPS_STORAGE_KEY) || '{}') }
  catch { return {} }
}
// { groupId: boolean } — true/absent = expanded, false = collapsed. Absent
// (never toggled) defaults to expanded on first load, per spec.
const groupState = reactive(loadGroupState())

function toggleGroup(id) {
  groupState[id] = !(groupState[id] !== false)
  localStorage.setItem(NAV_GROUPS_STORAGE_KEY, JSON.stringify(groupState))
}
// A group containing the current route must always render expanded, even if
// the user previously collapsed it — never hide the active page's own link.
function groupHasActiveRoute(g) { return g.items.some((item) => inSection(item.to)) }
function isGroupOpen(g) {
  if (groupHasActiveRoute(g)) return true
  return groupState[g.id] !== false
}
</script>
