<template>
  <AuthShell
    portal="dealer"
    portal-name="Dealer Portal"
    :portal-icon="Truck"
    headline="Every vehicle, litre and trip — live."
    description="Track your fleet on the map, catch fuel theft the moment it happens and keep every pilot on schedule."
    :points="points"
    form-subtitle="Enter your details to open your fleet dashboard."
    submit-label="Sign in"
    security-note="Encrypted session · signs out automatically when idle"
    note="Need an account? Ask your Aayunex administrator."
    :busy="busy"
    :error="error"
    @submit="submit"
  />
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { BellRing, Fuel, MapPinned, Truck } from 'lucide-vue-next'
import AuthShell from '@shared/ui/AuthShell.vue'
import { login, justLoggedIn } from '../auth'

const points = [
  { icon: MapPinned, title: 'Live tracking', text: 'GPS position, routes and trip history.' },
  { icon: Fuel, title: 'Fuel security', text: 'Refuel and theft events as they happen.' },
  { icon: BellRing, title: 'Instant alerts', text: 'Overspeed, geofence and tamper events.' },
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
