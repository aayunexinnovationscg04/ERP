<template>
  <Toaster />
  <WelcomeGate v-if="justLoggedIn" :name="welcomeName" @done="justLoggedIn = false" />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <!-- phone top bar: brand + quick actions (theme, logout) — primary nav
         lives in the thumb-reachable bottom tab bar below, so there's no
         drawer/hamburger to manage -->
    <div class="mobilebar">
      <img :src="logo" alt="" class="mb-logo" />
      <span class="mb-brand-text"><span class="mb-brand-sub">Aayunex Innovations</span><span class="mb-brand">Fuel Guard X</span></span>
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
        <div class="brand side-brand">
          <img :src="logo" alt="" class="side-brand-logo" />
          <span class="label mb-brand-text"><span class="mb-brand-sub">Aayunex Innovations</span><span class="mb-brand">Fuel Guard X</span></span>
        </div>
        <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? ChevronsRight : ChevronsLeft" :size="16" :stroke-width="2.25" />
        </button>
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

      <div class="sidebar-controls">
        <button class="theme-toggle" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
          <Sun v-if="theme === 'dark'" :size="16" :stroke-width="2.25" />
          <Moon v-else :size="16" :stroke-width="2.25" />
        </button>
      </div>
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
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { motion, AnimatePresence } from 'motion-v'
import {
  Truck, Route, ChevronsLeft, ChevronsRight, PowerOff,
  Sun, Moon, ChevronDown, User, ShieldAlert, Compass, Navigation,
} from 'lucide-vue-next'
import Toaster from './components/Toaster.vue'
import WelcomeGate from './components/WelcomeGate.vue'
import { auth, clearAuth, justLoggedIn } from './auth'
import { usePrefersReducedMotion, pageTransition } from './motion'
import { useTheme } from './theme'
import logo from './assets/logo.png'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const welcomeName = computed(() => {
  const u = auth.user?.username
  return u ? u.charAt(0).toUpperCase() + u.slice(1) : 'Pilot'
})
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
function groupHasActiveRoute(g) {
  return g.items.some((item) => route.path === item.to)
}

// Accordion: at most ONE group open at a time. Navigating to a page
// auto-opens its group (so the active link is never hidden on arrival),
// but afterward the toggle is a real toggle — clicking an open group
// (including the active one) closes it, and it only re-opens on the next
// navigation into that section.
const initialGroup = navGroups.find(groupHasActiveRoute)?.key
  ?? localStorage.getItem(NAV_GROUPS_KEY)
  ?? navGroups[0].key
const openGroupKey = ref(initialGroup)
watch(openGroupKey, (v) => localStorage.setItem(NAV_GROUPS_KEY, v || ''))
watch(() => route.path, () => {
  const g = navGroups.find(groupHasActiveRoute)
  if (g) openGroupKey.value = g.key
})

function isGroupOpen(g) {
  return openGroupKey.value === g.key
}
function toggleGroup(g) {
  openGroupKey.value = openGroupKey.value === g.key ? null : g.key
}
</script>
