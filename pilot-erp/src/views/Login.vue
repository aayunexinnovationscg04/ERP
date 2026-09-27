<template>
  <AuthShell
    portal="pilot"
    portal-name="Pilot App"
    :portal-icon="Navigation"
    headline="Your truck, your route, your day."
    description="Your assigned vehicle, today's trips and safety alerts — built for the phone in your cab."
    :points="points"
    form-subtitle="Sign in with the details your fleet manager gave you."
    submit-label="Sign in"
    security-note="Encrypted session · stays signed in on this phone"
    note="Forgot your password? Contact your fleet manager."
    :busy="busy"
    :error="error"
    @submit="submit"
  />
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Navigation, Route, ShieldAlert, Truck } from 'lucide-vue-next'
import AuthShell from '@shared/ui/AuthShell.vue'
import { login, justLoggedIn } from '../auth'

const points = [
  { icon: Truck, title: 'My vehicle', text: 'Live location and status of your truck.' },
  { icon: Route, title: 'Trips', text: "Today's route and your trip history." },
  { icon: ShieldAlert, title: 'Safety alerts', text: 'Know the moment something is wrong.' },
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
