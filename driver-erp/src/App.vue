<template>
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="shell">
    <header class="appbar">
      <div class="brand">⛽ <span>Fuel Guard X</span></div>
      <div class="who">{{ auth.user?.username }}</div>
    </header>

    <main class="screen"><router-view /></main>

    <nav class="tabbar">
      <router-link to="/" class="tab">
        <span class="ic">🚚</span><span>My Truck</span>
      </router-link>
      <router-link to="/trips" class="tab">
        <span class="ic">🛣️</span><span>Trips</span>
      </router-link>
      <router-link to="/alerts" class="tab">
        <span class="ic">🔔</span><span>Alerts</span>
      </router-link>
      <a class="tab" @click="logout">
        <span class="ic">⏻</span><span>Log out</span>
      </a>
    </nav>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { auth, clearAuth } from './auth'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
function logout() { clearAuth(); router.push('/login') }
</script>
