<template>
  <div class="loginwrap">
    <div class="card loginbox">
      <div class="brand" style="margin-bottom:6px">⛽ <span>Fuel Guard X</span></div>
      <div class="muted" style="margin-bottom:22px">Driver sign in</div>
      <form @submit.prevent="submit">
        <label class="muted" style="font-size:12px">Username</label>
        <input v-model="username" autocomplete="username" autocapitalize="none" style="margin:6px 0 14px" />
        <label class="muted" style="font-size:12px">Password</label>
        <input v-model="password" type="password" autocomplete="current-password" style="margin:6px 0 18px" />
        <button class="primary" :disabled="loading">{{ loading ? 'Signing in…' : 'Sign in' }}</button>
        <div v-if="error" class="err">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, getMe } from '../api'
import { setAuth } from '../auth'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const data = await login(username.value.trim(), password.value)
    setAuth({ access: data.access, refresh: data.refresh, user: data.user })
    try { const me = await getMe(); setAuth({ user: me }) } catch (e) { /* non-fatal */ }
    router.push('/')
  } catch (e) {
    error.value = e.response?.status === 429
      ? 'Too many attempts. Please wait a minute and try again.'
      : (e.response?.data?.detail || 'Invalid username or password.')
  } finally {
    loading.value = false
  }
}
</script>
