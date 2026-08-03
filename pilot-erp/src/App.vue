<template>
  <Toaster />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <!-- phone top bar: brand only — primary nav lives in the thumb-reachable
         bottom tab bar below, so there's no drawer/hamburger to manage -->
    <div class="mobilebar">
      <img :src="logo" alt="" class="mb-logo" />
      <span class="mb-brand">Fuel Guard X</span>
      <span class="mb-user">{{ auth.user?.username }}</span>
    </div>

    <!-- desktop/tablet: collapsible side navbar -->
    <aside class="sidebar">
      <div class="side-head">
        <div class="brand side-brand"><img :src="logo" alt="" class="side-brand-logo" /> <span class="label">Fuel Guard X</span></div>
        <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? ChevronsRight : ChevronsLeft" :size="16" />
        </button>
      </div>
      <nav class="nav">
        <router-link to="/" title="My Truck"><Truck :size="18" class="ic" /><span class="label">My Truck</span></router-link>
        <router-link to="/trips" title="Trips"><Route :size="18" class="ic" /><span class="label">Trips</span></router-link>
        <router-link to="/alerts" title="Alerts"><Bell :size="18" class="ic" /><span class="label">Alerts</span></router-link>
      </nav>
      <div class="spacer" style="flex:1"></div>
      <div class="muted label side-user" style="font-size:12px">{{ auth.user?.username }} · pilot</div>
      <button class="logout-btn" style="margin-top:12px" @click="logout" title="Log out">
        <PowerOff :size="16" class="ic" /><span class="label">Log out</span>
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

    <!-- phone-only bottom tab bar: thumb-reachable primary nav + logout -->
    <nav class="tabbar">
      <router-link to="/" title="My Truck"><span class="tab-ic"><Truck :size="20" /></span>My Truck</router-link>
      <router-link to="/trips" title="Trips"><span class="tab-ic"><Route :size="20" /></span>Trips</router-link>
      <router-link to="/alerts" title="Alerts"><span class="tab-ic"><Bell :size="20" /></span>Alerts</router-link>
      <a href="#" title="Log out" @click.prevent="logout"><span class="tab-ic"><PowerOff :size="20" /></span>Log out</a>
    </nav>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { motion, AnimatePresence } from 'motion-v'
import { Truck, Route, Bell, ChevronsLeft, ChevronsRight, PowerOff } from 'lucide-vue-next'
import Toaster from './components/Toaster.vue'
import { auth, clearAuth } from './auth'
import { usePrefersReducedMotion, pageTransition } from './motion'
import logo from './assets/logo.png'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const collapsed = ref(localStorage.getItem('fgx-pilot-sidebar-collapsed') === '1')
const reduced = usePrefersReducedMotion()
watch(collapsed, (v) => localStorage.setItem('fgx-pilot-sidebar-collapsed', v ? '1' : '0'))
function logout() { clearAuth(); router.push('/login') }
</script>
