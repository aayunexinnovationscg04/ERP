<template>
  <Toaster />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app">
    <div class="mobilebar">
      <button class="hamburger" @click="menuOpen = true" aria-label="Open menu"><Menu :size="22" /></button>
      <div class="brand"><img class="brand-logo" src="./assets/logo.png" alt="" /> <span class="brand-title">Admin</span></div>
    </div>
    <div class="backdrop" :class="{ open: menuOpen }" @click="menuOpen = false"></div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand">
        <img class="brand-logo" src="./assets/logo.png" alt="Fuel Guard X" />
        <div class="brand-text">
          <span class="brand-title">Control Tower</span>
          <span class="brand-sub">Admin ERP</span>
        </div>
        <button
          type="button" class="theme-toggle" @click="toggleTheme"
          :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
          :aria-label="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
        >
          <Sun v-if="theme === 'dark'" :size="18" />
          <Moon v-else :size="18" />
        </button>
      </div>
      <nav class="nav">
        <template v-for="(g, gi) in navGroups" :key="g.key">
          <div class="nav-group" :class="{ collapsed: !isExpanded(g) }">
            <button
              type="button" class="nav-group-head" @click="toggleGroup(g)"
              :aria-expanded="isExpanded(g)"
            >
              <span class="grp-ic"><component :is="g.icon" :size="15" /></span>
              <span class="nav-group-label">{{ g.label }}</span>
              <span class="chev"><ChevronDown :size="14" /></span>
            </button>
            <div class="nav-group-items" v-show="isExpanded(g)">
              <router-link v-for="item in g.items" :key="item.to" :to="item.to" @click="menuOpen = false">
                <span class="ic"><component :is="item.icon" :size="18" /></span> {{ item.label }}
              </router-link>
            </div>
          </div>
          <div class="nav-divider" v-if="gi < navGroups.length - 1"></div>
        </template>
      </nav>
      <div style="flex:1"></div>
      <button class="logout-btn" style="margin-top:12px;background:rgba(255,255,255,.06);border-color:var(--ink-border);color:var(--ink-text)" @click="logout">Log out</button>
    </aside>
    <main class="main">
      <AnimatePresence mode="wait">
        <motion.div
          :key="$route.fullPath"
          :initial="{ opacity: 0, y: reduced ? 0 : 8 }"
          :animate="{ opacity: 1, y: 0 }"
          :exit="{ opacity: 0, y: reduced ? 0 : -6 }"
          :transition="{ duration: reduced ? 0 : 0.18, ease: [0.4, 0, 0.2, 1] }"
        >
          <router-view />
        </motion.div>
      </AnimatePresence>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { motion, AnimatePresence } from 'motion-v'
import {
  Menu, Users, KeyRound, Activity, Sun, Moon, ChevronDown,
  Building2, BarChart, Truck, Radar, Cpu, Server, ScrollText,
  ShieldAlert, Flame, ChartLine,
} from 'lucide-vue-next'
import { auth, clearAuth } from './auth'
import { useTheme } from './theme'
import Toaster from './components/Toaster.vue'
const route = useRoute(); const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
const { theme, toggleTheme } = useTheme()
const reduced = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false
watch(() => route.path, () => { menuOpen.value = false })
function logout() { clearAuth(); router.push('/login') }

// ---- grouped, collapsible sidebar nav ----
const navGroups = [
  {
    key: 'company', label: 'Company Management', icon: Building2,
    items: [
      { to: '/companies', label: 'Companies', icon: Building2 },
      { to: '/company-analytics', label: 'Company Analytics', icon: BarChart },
    ],
  },
  {
    key: 'user', label: 'User Management', icon: Users,
    items: [
      { to: '/users', label: 'Users', icon: Users },
      { to: '/roles', label: 'Role Management', icon: KeyRound },
    ],
  },
  {
    key: 'fleet', label: 'Global Fleet Monitoring', icon: Truck,
    items: [
      { to: '/fleet-monitoring', label: 'Fleet Overview', icon: Radar },
    ],
  },
  {
    key: 'device', label: 'Device Management', icon: Cpu,
    items: [
      { to: '/devices', label: 'Devices', icon: Cpu },
    ],
  },
  {
    key: 'platform', label: 'Platform Monitoring', icon: Server,
    items: [
      { to: '/platform', label: 'Platform Health', icon: Activity },
      { to: '/platform-logs', label: 'Audit & Error Logs', icon: ScrollText },
    ],
  },
  {
    key: 'security', label: 'Security & Analytics', icon: ShieldAlert,
    items: [
      { to: '/security-analytics', label: 'Fraud & Fuel Theft Analytics', icon: Flame },
      { to: '/reports', label: 'Global Reports', icon: ChartLine },
    ],
  },
]

const GROUP_STORAGE_KEY = 'fgx_admin_nav_groups'
function groupHasActiveRoute(g) {
  return g.items.some((i) => route.path === i.to || route.path.startsWith(i.to + '/'))
}

// Accordion: at most ONE group open at a time, so the sidebar never grows
// tall enough to need scrolling — opening a group closes whichever was open.
// Defaults to whichever group contains the current route (falls back to the
// first group), not "everything expanded".
const initialGroup = navGroups.find(groupHasActiveRoute)?.key
  ?? localStorage.getItem(GROUP_STORAGE_KEY)
  ?? navGroups[0].key
const openGroupKey = ref(initialGroup)
watch(openGroupKey, (v) => localStorage.setItem(GROUP_STORAGE_KEY, v || ''))

// a group containing the active route always renders expanded, regardless of
// the accordion's open/closed state
function isExpanded(g) {
  return groupHasActiveRoute(g) || openGroupKey.value === g.key
}
function toggleGroup(g) {
  openGroupKey.value = openGroupKey.value === g.key ? null : g.key
}
</script>
