<template>
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app">
    <div class="mobilebar">
      <button class="hamburger" aria-label="Menu" @click="menuOpen = true">☰</button>
      <div class="brand">⛽ <span>Fuel Guard X</span></div>
    </div>
    <div class="backdrop" :class="{ open: menuOpen }" @click="menuOpen = false"></div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand">⛽ <span>Fuel Guard X</span></div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/">Dashboard</router-link>
        <router-link to="/fleet">Fleet</router-link>
        <router-link to="/alerts">Alerts</router-link>
      </nav>
      <div class="spacer" style="flex:1"></div>
      <div class="muted" style="font-size:12px">
        {{ auth.user?.company?.name }}<br />
        {{ auth.user?.username }} · {{ auth.user?.role }}
      </div>
      <button style="margin-top:12px" @click="logout">Log out</button>
    </aside>
    <main class="main"><router-view /></main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { auth, clearAuth } from './auth'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
watch(() => route.path, () => { menuOpen.value = false })
function logout() { clearAuth(); router.push('/login') }
</script>
