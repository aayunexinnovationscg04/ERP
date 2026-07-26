<template>
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app">
    <div class="mobilebar">
      <button class="hamburger" @click="menuOpen = true" aria-label="Open menu">☰</button>
      <div class="brand">🛡️ <span>Super Admin</span></div>
    </div>
    <div class="backdrop" :class="{ open: menuOpen }" @click="menuOpen = false"></div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand">🛡️ <span>Super Admin</span></div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/users">Users</router-link>
        <router-link to="/roles">Role Management</router-link>
      </nav>
      <div style="flex:1"></div>
      <div class="muted" style="font-size:12px">{{ auth.user?.username }} · superadmin</div>
      <button style="margin-top:12px" @click="logout">Log out</button>
    </aside>
    <main class="main"><router-view /></main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { auth, clearAuth } from './auth'
const route = useRoute(); const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
watch(() => route.path, () => { menuOpen.value = false })
function logout() { clearAuth(); router.push('/login') }
</script>
