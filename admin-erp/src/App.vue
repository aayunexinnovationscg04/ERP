<template>
  <Toaster />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app">
    <div class="mobilebar">
      <button class="hamburger" @click="menuOpen = true" aria-label="Open menu"><Menu :size="22" /></button>
      <div class="brand"><ShieldCheck :size="18" /> <span>Super Admin</span></div>
    </div>
    <div class="backdrop" :class="{ open: menuOpen }" @click="menuOpen = false"></div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand"><ShieldCheck :size="20" /> <span>Super Admin</span></div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/users"><Users :size="18" class="ic" /> Users</router-link>
        <router-link to="/roles"><KeyRound :size="18" class="ic" /> Role Management</router-link>
        <router-link to="/platform"><Activity :size="18" class="ic" /> Platform</router-link>
      </nav>
      <div style="flex:1"></div>
      <div class="muted" style="font-size:12px">{{ auth.user?.username }} · superadmin</div>
      <button style="margin-top:12px" @click="logout">Log out</button>
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
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Menu, ShieldCheck, Users, KeyRound, Activity } from 'lucide-vue-next'
import { auth, clearAuth } from './auth'
import Toaster from './components/Toaster.vue'
const route = useRoute(); const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
watch(() => route.path, () => { menuOpen.value = false })
function logout() { clearAuth(); router.push('/login') }
</script>
