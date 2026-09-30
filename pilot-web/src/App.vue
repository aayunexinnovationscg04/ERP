<template>
  <Toaster />
  <WelcomeGate v-if="justLoggedIn" :name="welcomeName" @done="justLoggedIn = false" />
  <div v-if="isLogin"><router-view /></div>
  <div v-else-if="showShell" class="app" :class="{ collapsed }">
    <div class="scrim" :class="{ show: menuOpen }" @click="menuOpen = false" aria-hidden="true"></div>

    <aside class="sidebar" :class="{ open: menuOpen }" aria-label="Main navigation">
      <div class="sb-brand">
        <router-link :to="homePath" class="sb-home" title="Fuel Guard X">
          <span class="sb-logo"><img :src="logo" alt="AAYUNEX INNOVATIONS OPC Pvt Ltd. logo" /></span>
          <span class="sb-name"><strong>Fuel Guard X</strong><small>Pilot App</small></span>
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
            <span v-if="item.to === '/alerts' && openAlerts" class="nav-count" :aria-label="`${openAlerts} open alerts`">{{ openAlerts > 99 ? '99+' : openAlerts }}</span>
          </router-link>
        </section>
        <PortalStrip />
      </nav>

      <div class="sb-foot">
        <div class="sb-user" :title="collapsed ? userName : undefined">
          <span class="avatar">{{ initials }}</span>
          <span class="sb-user-text">
            <strong>{{ userName }}</strong>
            <small>{{ roleLabel }}</small>
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
          <router-link v-if="canOpen('/alerts')" to="/alerts" class="tb-btn tb-alerts" :title="openAlerts ? `${openAlerts} open alert(s)` : 'Alerts'"
                       :aria-label="openAlerts ? `${openAlerts} open alerts` : 'Alerts'">
            <Bell :size="18" />
            <span v-if="openAlerts" class="dotcount">{{ openAlerts > 99 ? '99+' : openAlerts }}</span>
          </router-link>
          <button type="button" class="tb-btn tb-theme" @click="toggleTheme" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
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
          <PageSkeleton v-if="showRouteSkeleton" />
          <div v-else :key="$route.fullPath" class="page-in">
            <router-view v-slot="{ Component }"><component :is="Component" /></router-view>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Truck, Route, Navigation, Compass, ShieldAlert, User, Bell, Menu, X, ArrowLeft, ChevronRight,
  PanelLeftClose, PanelLeftOpen, LogOut, Sun, Moon, Eye,
} from 'lucide-vue-next'
import PortalStrip from './components/PortalStrip.vue'
import Toaster from './components/Toaster.vue'
import WelcomeGate from './components/WelcomeGate.vue'
import PageSkeleton from './components/PageSkeleton.vue'
import { auth, justLoggedIn, logout as endSession } from './auth'
import { getSummary } from './api'
import { useTheme } from './theme'
import logo from '@shared/design/brand/aayunex-logo.png'
import { canOpen, firstAllowedPath } from './access'

const route = useRoute()
const router = useRouter()
// Nothing of the signed-in app may ever flash before sign-in: until the router
// has settled the first navigation (session restore + auth guard) render
// nothing, then show public pages (login, view-as) alone and the app shell
// only for a signed-in user.
const routerReady = ref(false)
router.isReady().then(() => { routerReady.value = true })
const isLogin = computed(() => routerReady.value && !!route.meta.public)
const showShell = computed(() => routerReady.value && !route.meta.public && auth.isAuthed)
const welcomeName = computed(() => {
  const u = auth.user?.username
  return u ? u.charAt(0).toUpperCase() + u.slice(1) : 'Pilot'
})
const userName = computed(() => {
  const u = auth.user
  if (!u) return 'Pilot'
  const full = [u.first_name, u.last_name].filter(Boolean).join(' ')
  return full || u.username || 'Pilot'
})
const initials = computed(() => {
  const parts = (userName.value || '?').replace(/[^A-Za-z0-9 ]/g, ' ').trim().split(/\s+/)
  return ((parts[0]?.[0] || '?') + (parts[1]?.[0] || '')).toUpperCase()
})
const roleLabel = computed(() => {
  const c = auth.user?.company?.name
  return c ? `Pilot · ${c}` : 'Pilot'
})

const menuOpen = ref(false)
const collapsed = ref(localStorage.getItem('fgx-pilot-sidebar-collapsed') === '1')
watch(collapsed, (v) => localStorage.setItem('fgx-pilot-sidebar-collapsed', v ? '1' : '0'))
const { theme, toggleTheme } = useTheme()

// The document scrolls; start each page at the top and close the phone drawer.
watch(() => route.path, () => { menuOpen.value = false; window.scrollTo({ top: 0, left: 0 }); revealActiveLink() })
// The nav scrolls on short screens: keep the current page's link in view.
function revealActiveLink() {
  nextTick(() => document.querySelector('.sb-nav .sb-link.router-link-active')?.scrollIntoView({ block: 'nearest' }))
}
onMounted(revealActiveLink)
watch(menuOpen, (open) => { document.documentElement.classList.toggle('drawer-open', open) })
function onKey(e) { if (e.key === 'Escape' && menuOpen.value) menuOpen.value = false }
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => { window.removeEventListener('keydown', onKey); document.documentElement.classList.remove('drawer-open') })
function onNavClick(e) { if (e.target.closest('a')) menuOpen.value = false }

const NAV_GROUPS = [
  { id: 'vehicle', label: 'Vehicle', items: [{ to: '/', label: 'My Truck', icon: Truck }] },
  {
    id: 'trips', label: 'Trips',
    items: [
      { to: '/trips', label: 'Trips', icon: Route },
      { to: '/route-guidance', label: 'Route Guidance', icon: Navigation },
      { to: '/navigation', label: 'Traffic & Delays', icon: Compass },
    ],
  },
  { id: 'safety', label: 'Safety', items: [{ to: '/alerts', label: 'Alerts', icon: ShieldAlert }] },
  { id: 'account', label: 'Account', items: [{ to: '/profile', label: 'Profile', icon: User }] },
]
// '/' only matches itself; other items also stay lit on their sub-paths.
function inSection(base) { return base === '/' ? route.path === '/' : route.path === base || route.path.startsWith(base + '/') }

// Only screens this pilot may open (Role Management modules).
const visibleGroups = computed(() => NAV_GROUPS
  .map((g) => ({ ...g, items: g.items.filter((i) => canOpen(i.to)) }))
  .filter((g) => g.items.length))
const homePath = computed(() => (auth.user ? firstAllowedPath() : '/'))

// Breadcrumb names the page (pages carry no big title of their own).
const crumb = computed(() => {
  for (const g of NAV_GROUPS) {
    const item = g.items.find((i) => inSection(i.to))
    if (!item) continue
    if (route.path === item.to) return { group: g.label, page: item.label }
    return { group: item.label, parentTo: item.to, page: 'Details' }
  }
  return null
})

// Open-alert count for the Alerts link + top-bar bell (same /pilot/summary the
// home page reads), refreshed on every navigation.
const openAlerts = ref(0)
async function refreshCount() {
  if (!auth.isAuthed || isLogin.value) return
  try { openAlerts.value = (await getSummary()).open_alerts || 0 } catch (e) { /* keep last */ }
}
watch([() => route.path, () => auth.isAuthed], () => { refreshCount() }, { immediate: true })

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

async function logout() { openAlerts.value = 0; menuOpen.value = false; await endSession(); router.push('/login') }

// view-as tab: closing it ends the read-only session
function closeView() { endSession() }
</script>
