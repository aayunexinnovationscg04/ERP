<template>
  <Toaster />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app" :class="{ collapsed }">
    <div class="mobilebar">
      <button class="hamburger" aria-label="Menu" @click="menuOpen = !menuOpen"><Menu :size="22" /></button>
    </div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="side-head">
        <div class="brand side-brand"><img :src="logo" alt="" class="side-brand-logo" /> <span class="label">Fuel Guard X</span></div>
        <button class="collapse-btn" @click="collapsed = !collapsed" :title="collapsed ? 'Expand sidebar' : 'Collapse sidebar'">
          <component :is="collapsed ? ChevronsRight : ChevronsLeft" :size="16" />
        </button>
      </div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/" title="My Truck"><Truck :size="18" class="ic" /><span class="label">My Truck</span></router-link>
        <router-link to="/trips" title="Trips"><Route :size="18" class="ic" /><span class="label">Trips</span></router-link>
        <router-link to="/alerts" title="Alerts"><Bell :size="18" class="ic" /><span class="label">Alerts</span></router-link>
      </nav>
      <div class="spacer" style="flex:1"></div>
      <div class="muted label side-user" style="font-size:12px">{{ auth.user?.username }} · driver</div>
      <button class="logout-btn" style="margin-top:12px" @click="logout" title="Log out">
        <PowerOff :size="16" class="ic" /><span class="label">Log out</span>
      </button>
    </aside>

    <main class="main">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <div :key="$route.fullPath"><component :is="Component" /></div>
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, Truck, Route, Bell, ChevronsLeft, ChevronsRight, PowerOff } from 'lucide-vue-next'
import Toaster from './components/Toaster.vue'
import { auth, clearAuth } from './auth'
import logo from './assets/logo.png'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
const collapsed = ref(localStorage.getItem('fgx-driver-sidebar-collapsed') === '1')
watch(() => route.path, () => { menuOpen.value = false })
watch(collapsed, (v) => localStorage.setItem('fgx-driver-sidebar-collapsed', v ? '1' : '0'))
function logout() { clearAuth(); router.push('/login') }
</script>
