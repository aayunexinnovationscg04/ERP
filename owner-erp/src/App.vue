<template>
  <Toaster />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app">
    <div class="mobilebar">
      <button class="hamburger" aria-label="Menu" @click="menuOpen = true"><Menu :size="22" /></button>
      <div class="brand"><Fuel :size="18" /> <span>Fuel Guard X</span></div>
    </div>
    <div class="backdrop" :class="{ open: menuOpen }" @click="menuOpen = false"></div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand side-brand"><Fuel :size="20" /> <span>Fuel Guard X</span></div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/"><LayoutDashboard :size="18" class="ic" /> Dashboard</router-link>
        <router-link to="/fleet"><Truck :size="18" class="ic" /> Fleet</router-link>
        <router-link to="/alerts"><Bell :size="18" class="ic" /> Alerts</router-link>
        <router-link to="/geofences"><MapPin :size="18" class="ic" /> Geofences</router-link>
      </nav>
      <div class="spacer" style="flex:1"></div>
      <div class="muted" style="font-size:12px">
        {{ auth.user?.company?.name }}<br />
        {{ auth.user?.username }} · {{ auth.user?.role }}
      </div>
      <button style="margin-top:12px" @click="logout">Log out</button>
    </aside>
    <main class="main">
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in"><component :is="Component" /></transition>
      </router-view>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, Fuel, LayoutDashboard, Truck, Bell, MapPin } from 'lucide-vue-next'
import { auth, clearAuth } from './auth'
import Toaster from './components/Toaster.vue'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
watch(() => route.path, () => { menuOpen.value = false })
function logout() { clearAuth(); router.push('/login') }
</script>
