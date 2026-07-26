<template>
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app">
    <!-- mobile top bar with hamburger (hidden on desktop) -->
    <header class="mobilebar">
      <button class="hamburger" aria-label="Open menu" @click="menuOpen = true">☰</button>
      <div class="brand">⛽ <span>Fuel Guard X</span></div>
      <div class="spacer"></div>
    </header>

    <!-- drawer backdrop (mobile only) -->
    <div class="backdrop" :class="{ show: menuOpen }" @click="menuOpen = false"></div>

    <!-- side navbar (desktop) / slide-in drawer (mobile) -->
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand side-brand">⛽ <span>Fuel Guard X</span></div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/"><span class="ic">🚚</span> My Truck</router-link>
        <router-link to="/trips"><span class="ic">🛣️</span> Trips</router-link>
        <router-link to="/alerts"><span class="ic">🔔</span> Alerts</router-link>
      </nav>
      <div class="spacer" style="flex:1"></div>
      <div class="muted" style="font-size:12px">{{ auth.user?.username }} · driver</div>
      <button style="margin-top:12px" @click="logout">Log out</button>
    </aside>

    <main class="main"><router-view /></main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { auth, clearAuth } from './auth'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
watch(() => route.path, () => { menuOpen.value = false })
function logout() { clearAuth(); router.push('/login') }
</script>
