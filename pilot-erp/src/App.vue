<template>
  <Toaster />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <!-- phone top bar: brand + quick actions (theme, logout) — primary nav
         lives in the thumb-reachable bottom tab bar below, so there's no
         drawer/hamburger to manage -->
    <div class="mobilebar">
      <img :src="logo" alt="" class="mb-logo" />
      <span class="mb-brand">Fuel Guard X</span>
      <span class="spacer"></span>
      <span class="mb-user">{{ auth.user?.username }}</span>
      <button class="theme-toggle mb-theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
        <Sun v-if="theme === 'dark'" :size="18" />
        <Moon v-else :size="18" />
      </button>
      <button class="mb-logout" @click="logout" title="Log out">
        <PowerOff :size="18" :stroke-width="2.25" />
      </button>
    </div>

    <!-- desktop/tablet: collapsible side navbar, grouped into clusters -->
    <aside class="sidebar">
      <div class="side-head">
        <div class="brand side-brand"><img :src="logo" alt="" class="side-brand-logo" /> <span class="label">Fuel Guard X</span></div>
        <div class="side-head-actions">
          <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
            <Sun v-if="theme === 'dark'" :size="16" :stroke-width="2.25" />
            <Moon v-else :size="16" :stroke-width="2.25" />
          </button>
          <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
            <component :is="collapsed ? ChevronsRight : ChevronsLeft" :size="16" :stroke-width="2.25" />
          </button>
        </div>
      </div>

      <nav class="nav nav-grouped">
        <div v-for="g in navGroups" :key="g.key" class="nav-group">
          <button type="button" class="nav-group-head" @click="toggleGroup(g)" :aria-expanded="isGroupOpen(g)">
            <component :is="g.icon" :size="14" :stroke-width="2.25" class="nav-group-ic" />
            <span class="label nav-group-label">{{ g.label }}</span>
            <span class="spacer"></span>
            <ChevronDown :size="14" :stroke-width="2.25" class="nav-group-chevron" :class="{ open: isGroupOpen(g) }" />
          </button>
          <div class="nav-group-items" v-show="isGroupOpen(g)">
            <router-link v-for="item in g.items" :key="item.to" :to="item.to" :title="item.label">
              <component :is="item.icon" :size="18" :stroke-width="2.25" class="ic" />
              <span class="label">{{ item.label }}</span>
            </router-link>
          </div>
        </div>
      </nav>

      <div class="spacer" style="flex:1"></div>
      <button class="logout-btn" style="margin-top:12px" @click="logout" title="Log out">
        <PowerOff :size="16" :stroke-width="2.25" class="ic" /><span class="label">Log out</span>
      </button>
    </aside>

    <main class="main">
      <AnimatePresence mode="wait">
        <motion.div :key="$route.fullPath"
          :initial="{ opacity: 0, y: reduced ? 0 : 8 }"
          :animate="{ opacity: 1, y: 0 }"
          :exit="{ opacity: 0, y: reduced ? 0 : -6 }"
          :transition="pageTransition(reduced)">
          <router-view v-slot="{ Component }">
            <component :is="Component" />
          </router-view>
        </motion.div>
      </AnimatePresence>
    </main>

    <!-- phone-only bottom tab bar: thumb-reachable primary nav, capped at 5
         icons — one per top-level cluster (Route Guidance lives inside Trip
         Operations on desktop / off the Trips page on mobile, not its own tab) -->
    <nav class="tabbar">
      <router-link to="/" title="My Truck"><span class="tab-ic"><Truck :size="20" :stroke-width="2.25" /></span>My Truck</router-link>
      <router-link to="/trips" title="Trips"><span class="tab-ic"><Route :size="20" :stroke-width="2.25" /></span>Trips</router-link>
      <router-link to="/navigation" title="Navigation"><span class="tab-ic"><Compass :size="20" :stroke-width="2.25" /></span>Navigation</router-link>
      <router-link to="/alerts" title="Alerts"><span class="tab-ic"><ShieldAlert :size="20" :stroke-width="2.25" /></span>Alerts</router-link>
      <router-link to="/profile" title="Profile"><span class="tab-ic"><User :size="20" :stroke-width="2.25" /></span>Profile</router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { motion, AnimatePresence } from 'motion-v'
import {
  Truck, Route, ChevronsLeft, ChevronsRight, PowerOff,
  Sun, Moon, ChevronDown, User, ShieldAlert, Compass, Navigation,
} from 'lucide-vue-next'
import Toaster from './components/Toaster.vue'
import { auth, clearAuth } from './auth'
import { usePrefersReducedMotion, pageTransition } from './motion'
import { useTheme } from './theme'
import logo from './assets/logo.png'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const collapsed = ref(localStorage.getItem('fgx-pilot-sidebar-collapsed') === '1')
const reduced = usePrefersReducedMotion()
const { theme, toggleTheme } = useTheme()
watch(collapsed, (v) => localStorage.setItem('fgx-pilot-sidebar-collapsed', v ? '1' : '0'))
function logout() { clearAuth(); router.push('/login') }

// ---- desktop sidebar: grouped nav clusters ----
const navGroups = [
  {
    key: 'vehicle', label: 'My Vehicle', icon: Truck,
    items: [{ to: '/', label: 'My Truck', icon: Truck }],
  },
  {
    key: 'trip-ops', label: 'Trip Operations', icon: Route,
    items: [
      { to: '/trips', label: 'Trips', icon: Route },
      { to: '/route-guidance', label: 'Route Guidance', icon: Navigation },
    ],
  },
  {
    key: 'profile', label: 'My Profile', icon: User,
    items: [{ to: '/profile', label: 'Profile', icon: User }],
  },
  {
    key: 'alerts', label: 'Alerts', icon: ShieldAlert,
    items: [{ to: '/alerts', label: 'Alerts', icon: ShieldAlert }],
  },
  {
    key: 'navigation', label: 'Navigation', icon: Compass,
    items: [{ to: '/navigation', label: 'Traffic & Delays', icon: Compass }],
  },
]

const NAV_GROUPS_KEY = 'fgx_pilot_nav_groups'
function loadGroupState() {
  try { return JSON.parse(localStorage.getItem(NAV_GROUPS_KEY) || '{}') } catch (e) { return {} }
}
const groupState = reactive(loadGroupState())
watch(groupState, (v) => localStorage.setItem(NAV_GROUPS_KEY, JSON.stringify(v)), { deep: true })

function groupHasActiveRoute(g) {
  return g.items.some((item) => route.path === item.to)
}
// default expanded; a group holding the active route always stays expanded
// regardless of stored/toggled state
function isGroupOpen(g) {
  if (groupHasActiveRoute(g)) return true
  return groupState[g.key] !== false
}
function toggleGroup(g) {
  groupState[g.key] = !isGroupOpen(g)
}
</script>
