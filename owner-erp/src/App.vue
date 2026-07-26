<template>
  <div v-if="isLogin"><router-view /></div>
  <div v-else class="app">
    <aside class="sidebar">
      <div class="brand">⛽ <span>Fuel Guard X</span></div>
      <nav class="nav">
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
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { auth, clearAuth } from './auth'

const route = useRoute()
const router = useRouter()
const isLogin = computed(() => route.path === '/login')
function logout() { clearAuth(); router.push('/login') }
</script>
