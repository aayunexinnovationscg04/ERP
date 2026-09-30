<template>
  <Toaster />
  <WelcomeGate v-if="justLoggedIn" :name="welcomeName" @done="justLoggedIn = false" />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <div class="scrim" :class="{ show: menuOpen }" @click="menuOpen = false" aria-hidden="true"></div>

    <aside class="sidebar" :class="{ open: menuOpen }" aria-label="Main navigation">
      <div class="sb-brand">
        <span class="sb-logo"><img :src="brandMark" alt="AAYUNEX INNOVATIONS OPC Pvt Ltd. logo" /></span>
        <div class="sb-name">
          <strong>Fuel Guard X</strong>
          <small>Admin Console</small>
        </div>
        <button
          type="button" class="sb-toggle" @click="collapsed = !collapsed"
          :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
        >
          <component :is="collapsed ? PanelLeftOpen : PanelLeftClose" :size="17" />
        </button>
        <button type="button" class="sb-close" @click="menuOpen = false" aria-label="Close menu"><X :size="20" /></button>
      </div>

      <nav class="sb-nav">
        <section v-for="g in navGroups" :key="g.key" class="sb-sec">
          <h2 class="sb-sec-title">{{ g.label }}</h2>
          <router-link
            v-for="item in g.items" :key="item.to" :to="item.to" class="sb-link"
            :title="collapsed ? item.label : undefined" @click="menuOpen = false"
          >
            <component :is="item.icon" :size="16" />
            <span class="label">{{ item.label }}</span>
          </router-link>
        </section>
        <PortalStrip />
      </nav>

      <div class="sb-foot">
        <div class="sb-user" :title="collapsed ? username : undefined">
          <span class="avatar">{{ initial }}</span>
          <div class="sb-user-text"><strong>{{ username }}</strong><small>Platform admin</small></div>
        </div>
        <button type="button" class="sb-icon-btn sb-logout" @click="logout" title="Sign out" aria-label="Sign out"><LogOut :size="17" /></button>
      </div>
    </aside>

    <div class="main-col">
      <header class="topbar">
        <button type="button" class="tb-btn tb-menu" @click="menuOpen = true" aria-label="Open menu"><Menu :size="22" /></button>
        <nav class="crumbs" aria-label="Breadcrumb">
          <template v-if="current.group && current.group !== current.page">
            <span class="c-group">{{ current.group }}</span>
            <ChevronRight class="c-sep" :size="14" />
          </template>
          <span class="c-page">{{ current.page }}</span>
        </nav>
        <div class="tb-spacer"></div>
        <div id="page-actions" class="tb-actions"></div>
        <div class="tb-right">
          <div class="user-menu" ref="userMenuEl">
            <button
              type="button" class="user-trigger" @click="userMenu = !userMenu"
              :aria-expanded="userMenu" aria-haspopup="menu" aria-label="Account menu"
            >
              <span class="avatar">{{ initial }}</span>
              <span class="ut-name">{{ username }}</span>
              <ChevronDown :size="15" />
            </button>
            <div v-if="userMenu" class="menu" role="menu">
              <div class="menu-head">
                <strong>{{ username }}</strong>
                <small>Platform administrator</small>
              </div>
              <button type="button" class="menu-item" role="menuitem" @click="askLogoutAll">
                <MonitorSmartphone :size="16" /> Sign out of all devices
              </button>
              <button type="button" class="menu-item danger" role="menuitem" @click="logout">
                <LogOut :size="16" /> Sign out
              </button>
            </div>
          </div>
        </div>
      </header>

      <main class="content">
        <PageSkeleton v-if="showRouteSkeleton" />
        <div v-else :key="$route.fullPath" class="page-in"><router-view /></div>
      </main>
    </div>

    <ConfirmDialog
      :open="confirmLogoutAll" title="Sign out of all devices?" tone="warn" confirm-label="Sign out everywhere"
      :busy="loggingOut" @cancel="confirmLogoutAll = false" @confirm="logoutAll"
    >
      This ends every admin, dealer and pilot session signed in with <b>{{ username }}</b>, on every browser and device — including this one.
    </ConfirmDialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Menu, X, Activity, ChevronDown, ChevronRight, LogOut,
  Building2, ChartColumn, Radar, Cpu, ScrollText, ShieldAlert, ChartLine,
  MonitorSmartphone, PanelLeftClose, PanelLeftOpen, RadioTower, Truck, Navigation,
} from 'lucide-vue-next'
import { auth, justLoggedIn, logout as endSession, logoutEverywhere } from './auth'
import './theme'  // pins the light theme
import PortalStrip from './components/PortalStrip.vue'
import Toaster from './components/Toaster.vue'
import WelcomeGate from './components/WelcomeGate.vue'
import PageSkeleton from './components/PageSkeleton.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import brandMark from '@shared/design/brand/aayunex-logo.png'

const route = useRoute(); const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const username = computed(() => auth.user?.username || 'admin')
const initial = computed(() => username.value.charAt(0).toUpperCase())
const welcomeName = computed(() => {
  const u = auth.user?.username
  return u ? u.charAt(0).toUpperCase() + u.slice(1) : 'Admin'
})

// Route chunks are lazy (router.js). A slow first-time chunk fetch shows a
// skeleton after 150ms instead of a frozen page.
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

const menuOpen = ref(false)
const userMenu = ref(false)
const userMenuEl = ref(null)
const collapsed = ref(localStorage.getItem('fgx-admin-sidebar-collapsed') === '1')
watch(collapsed, (v) => localStorage.setItem('fgx-admin-sidebar-collapsed', v ? '1' : '0'))

watch(() => route.path, () => {
  menuOpen.value = false; userMenu.value = false
  // the document is the scroller: start each page at the top
  window.scrollTo({ top: 0, left: 0 })
})
// The mobile drawer is modal: lock page scroll underneath while it's open.
watch(menuOpen, (v) => { document.body.style.overflow = v ? 'hidden' : '' })

function onKeydown(e) {
  if (e.key !== 'Escape') return
  menuOpen.value = false
  userMenu.value = false
}
function onDocClick(e) {
  if (userMenu.value && userMenuEl.value && !userMenuEl.value.contains(e.target)) userMenu.value = false
}
onMounted(() => { window.addEventListener('keydown', onKeydown); document.addEventListener('click', onDocClick) })
onBeforeUnmount(() => { window.removeEventListener('keydown', onKeydown); document.removeEventListener('click', onDocClick) })

async function logout() { userMenu.value = false; await endSession(); router.push('/login') }

const confirmLogoutAll = ref(false)
const loggingOut = ref(false)
function askLogoutAll() { userMenu.value = false; confirmLogoutAll.value = true }
async function logoutAll() {
  loggingOut.value = true
  try { await logoutEverywhere() } catch (e) { /* session is cleared locally either way */ }
  loggingOut.value = false
  confirmLogoutAll.value = false
  router.push('/login')
}

const navGroups = [
  {
    key: 'company', label: 'Companies',
    items: [
      { to: '/companies', label: 'Companies', icon: Building2 },
      { to: '/company-analytics', label: 'Company Analytics', icon: ChartColumn },
    ],
  },
  {
    key: 'user', label: 'Users & Access',
    items: [
      { to: '/dealers', label: 'Dealers', icon: Truck },
      { to: '/pilots', label: 'Pilots', icon: Navigation },
    ],
  },
  {
    key: 'fleet', label: 'Fleet & Devices',
    items: [
      { to: '/fleet-monitoring', label: 'Fleet Overview', icon: Radar },
      { to: '/devices', label: 'Devices', icon: Cpu },
      { to: '/device-data', label: 'Device data', icon: RadioTower },
    ],
  },
  {
    key: 'security', label: 'Security & Reports',
    items: [
      { to: '/security-analytics', label: 'Fraud & Theft Alerts', icon: ShieldAlert },
      { to: '/reports', label: 'Global Reports', icon: ChartLine },
    ],
  },
  {
    key: 'platform', label: 'Platform',
    items: [
      { to: '/platform', label: 'Platform Health', icon: Activity },
      { to: '/platform-logs', label: 'Audit & Error Logs', icon: ScrollText },
    ],
  },
]

const current = computed(() => {
  for (const g of navGroups) {
    const item = g.items.find((i) => route.path === i.to || route.path.startsWith(i.to + '/'))
    if (item) return { group: g.label, page: item.label }
  }
  return { group: '', page: 'Admin Console' }
})
</script>
