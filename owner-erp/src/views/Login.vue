<template>
  <div class="loginwrap">
    <div class="card loginbox">
      <div class="brand" style="justify-content:center">⛽ Fuel Guard X</div>
      <p class="muted" style="text-align:center;margin-top:-8px">Owner ERP</p>
      <form @submit.prevent="submit">
        <label class="muted">Username</label>
        <input v-model="username" autocomplete="username" style="margin:6px 0 14px" />
        <label class="muted">Password</label>
        <input v-model="password" type="password" autocomplete="current-password" style="margin:6px 0 18px" />
        <button class="primary" style="width:100%" :disabled="busy">
          {{ busy ? 'Signing in…' : 'Sign in' }}
        </button>
        <div v-if="error" class="err">{{ error }}</div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api'
import { setAuth } from '../auth'

const username = ref('')
const password = ref('')
const busy = ref(false)
const error = ref('')
const router = useRouter()

async function submit() {
  busy.value = true; error.value = ''
  try {
    const data = await login(username.value, password.value)
    setAuth({ access: data.access, refresh: data.refresh, user: data.user })
    router.push('/')
  } catch (e) {
    error.value = e.response?.status === 401 ? 'Invalid username or password.' : 'Login failed.'
  } finally { busy.value = false }
}
</script>
