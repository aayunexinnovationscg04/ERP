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
    </div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="side-head">
        <div class="brand side-brand"><img :src="logo" alt="" class="side-brand-logo" /> <span class="label">Fuel Guard X</span></div>
        <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? ChevronsRight : ChevronsLeft" :size="16" />
        </button>
      </div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/vehicles" title="Vehicles" :class="{ 'router-link-active': inSection('/vehicles') }"><Truck :size="18" class="ic" /><span class="label">Vehicles</span></router-link>
        <router-link to="/locations" title="Locations" :class="{ 'router-link-active': inSection('/locations') }"><LocateFixed :size="18" class="ic" /><span class="label">Locations</span></router-link>
        <router-link to="/fuel" title="Fuel" :class="{ 'router-link-active': inSection('/fuel') }"><Fuel :size="18" class="ic" /><span class="label">Fuel</span></router-link>
        <router-link to="/pilots" title="Pilots" :class="{ 'router-link-active': inSection('/pilots') }"><IdCard :size="18" class="ic" /><span class="label">Pilots</span></router-link>
        <router-link to="/alerts" title="Alerts" :class="{ 'router-link-active': inSection('/alerts') }"><Bell :size="18" class="ic" /><span class="label">Alerts</span></router-link>
        <router-link to="/geofences" title="Geofences" :class="{ 'router-link-active': inSection('/geofences') }"><MapPin :size="18" class="ic" /><span class="label">Geofences</span></router-link>
      </nav>
      <div class="spacer" style="flex:1"></div>
      <div class="muted label side-user" style="font-size:12px">
        {{ auth.user?.username }} · {{ auth.user?.role }}
      </div>
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
