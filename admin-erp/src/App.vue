<template>
  <Toaster />
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app">
    <div class="mobilebar">
      <button class="hamburger" @click="menuOpen = true" aria-label="Open menu"><Menu :size="22" /></button>
      <div class="brand"><img class="brand-logo" src="./assets/logo.png" alt="" /> <span class="brand-title">Admin</span></div>
    </div>
    <div class="backdrop" :class="{ open: menuOpen }" @click="menuOpen = false"></div>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <div class="brand">
        <img class="brand-logo" src="./assets/logo.png" alt="Fuel Guard X" />
        <div class="brand-text">
          <span class="brand-title">Control Tower</span>
          <span class="brand-sub">Admin ERP</span>
        </div>
      </div>
      <nav class="nav" @click="menuOpen = false">
        <router-link to="/users"><Users :size="18" class="ic" /> Users</router-link>
        <router-link to="/roles"><KeyRound :size="18" class="ic" /> Role Management</router-link>
        <router-link to="/platform"><Activity :size="18" class="ic" /> Platform</router-link>
      </nav>
      <div style="flex:1"></div>
      <div class="ico" style="font-size:12px;color:var(--ink-muted)">
        <span style="width:7px;height:7px;border-radius:50%;background:var(--brand-bright);flex:none;box-shadow:0 0 0 3px rgba(139,92,246,.25)"></span>
        {{ auth.user?.username }} · admin
      </div>
      <button class="logout-btn" style="margin-top:12px;background:rgba(255,255,255,.06);border-color:var(--ink-border);color:var(--ink-text)" @click="logout">Log out</button>
    </aside>
    <main class="main">
      <AnimatePresence mode="wait">
        <motion.div
          :key="$route.fullPath"
          :initial="{ opacity: 0, y: reduced ? 0 : 8 }"
          :animate="{ opacity: 1, y: 0 }"
          :exit="{ opacity: 0, y: reduced ? 0 : -6 }"
          :transition="{ duration: reduced ? 0 : 0.18, ease: [0.4, 0, 0.2, 1] }"
        >
          <router-view />
        </motion.div>
      </AnimatePresence>
    </main>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { motion, AnimatePresence } from 'motion-v'
import { Menu, Users, KeyRound, Activity } from 'lucide-vue-next'
import { auth, clearAuth } from './auth'
import Toaster from './components/Toaster.vue'
const route = useRoute(); const router = useRouter()
const isLogin = computed(() => route.path === '/login')
const menuOpen = ref(false)
const reduced = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false
watch(() => route.path, () => { menuOpen.value = false })
function logout() { clearAuth(); router.push('/login') }
</script>
