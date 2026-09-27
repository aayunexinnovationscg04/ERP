<template>
  <AuthShell
    portal="admin"
    portal-name="Admin Console"
    :portal-icon="ShieldCheck"
    headline="Run the whole Fuel Guard X platform from one console."
    description="Onboard companies, provision users and decide exactly which screens every role can open."
    :points="points"
    form-subtitle="Platform administrators only."
    submit-label="Sign in to console"
    security-note="Encrypted session · admin sign-in lasts at most 12 hours"
    note="Admin accounts are created internally — there is no self sign-up."
    :busy="busy"
    :error="error"
    @submit="submit"
  />
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Building2, KeyRound, ShieldCheck, UsersRound } from 'lucide-vue-next'
import AuthShell from '@shared/ui/AuthShell.vue'
import { login, justLoggedIn } from '../auth'

const points = [
  { icon: Building2, title: 'Companies', text: 'Onboard, review and suspend fleet operators.' },
  { icon: UsersRound, title: 'Users & roles', text: 'Admin, dealer, manager and pilot accounts.' },
  { icon: KeyRound, title: 'Access control', text: 'Per-role and per-person screen access.' },
]

const busy = ref(false)
const error = ref('')
const router = useRouter()
const route = useRoute()
// Only follow in-app paths, never an absolute URL (open-redirect guard).
const nextPath = () => {
  const n = route.query.next
  return typeof n === 'string' && n.startsWith('/') && !n.startsWith('//') ? n : '/'
}

async function submit({ username, password }) {
  busy.value = true
  error.value = ''
  try {
    await login(username, password)
    justLoggedIn.value = true
    router.replace(nextPath())
  } catch (e) {
    error.value = loginError(e)
  } finally {
    busy.value = false
  }
}

function loginError(e) {
  const s = e.response?.status
  if (s === 429) return 'Too many attempts. Please wait a minute and try again.'
  if (s === 403) return e.response.data?.detail || 'This account cannot sign in here.'
  if (s === 401) return 'Incorrect username or password.'
  return 'Could not reach the server. Check your connection and try again.'
}
</script>
