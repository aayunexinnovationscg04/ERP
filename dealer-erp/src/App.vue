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
    </div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="side-head">
        <div class="brand side-brand"><span class="logo-chip"><img :src="logo" alt="" class="side-brand-logo" /></span> <span class="label">Fuel Guard X</span></div>
        <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? ChevronsRight : ChevronsLeft" :size="16" />
        </button>
      </div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/vehicles" title="Vehicles" class="nav-vehicles" :class="{ 'router-link-active': inSection('/vehicles') }"><span class="ic"><Truck :size="18" /></span><span class="label">Vehicles</span></router-link>
        <router-link to="/locations" title="Locations" class="nav-locations" :class="{ 'router-link-active': inSection('/locations') }"><span class="ic"><LocateFixed :size="18" /></span><span class="label">Locations</span></router-link>
        <router-link to="/fuel" title="Fuel" class="nav-fuel" :class="{ 'router-link-active': inSection('/fuel') }"><span class="ic"><Fuel :size="18" /></span><span class="label">Fuel</span></router-link>
        <router-link to="/pilots" title="Pilots" class="nav-pilots" :class="{ 'router-link-active': inSection('/pilots') }"><span class="ic"><IdCard :size="18" /></span><span class="label">Pilots</span></router-link>
        <router-link to="/alerts" title="Alerts" class="nav-alerts" :class="{ 'router-link-active': inSection('/alerts') }"><span class="ic"><Bell :size="18" /></span><span class="label">Alerts</span></router-link>
        <router-link to="/geofences" title="Geofences" class="nav-geofences" :class="{ 'router-link-active': inSection('/geofences') }"><span class="ic"><MapPin :size="18" /></span><span class="label">Geofences</span></router-link>
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
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, X, LocateFixed, Truck, Bell, MapPin, Fuel, IdCard, ChevronsLeft, ChevronsRight, PowerOff } from 'lucide-vue-next'
import { motion, AnimatePresence, MotionConfig } from 'motion-v'
import { auth, clearAuth } from './auth'
import Toaster from './components/Toaster.vue'
import logo from './assets/logo.png'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
const collapsed = ref(localStorage.getItem('fgx-sidebar-collapsed') === '1')
watch(() => route.path, () => { menuOpen.value = false })
// The list routes and their /:id detail routes are flat siblings, not nested
// children, so vue-router's own router-link-active (matched-record based) drops
// once you're on e.g. /vehicles/123. Match by path prefix instead so the sidebar
// item stays highlighted while inside that section's detail pages.
function inSection(base) { return route.path === base || route.path.startsWith(base + '/') }
watch(collapsed, (v) => localStorage.setItem('fgx-sidebar-collapsed', v ? '1' : '0'))
function logout() { clearAuth(); router.push('/login') }
</script>
