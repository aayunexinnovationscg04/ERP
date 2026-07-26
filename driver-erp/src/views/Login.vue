<template>
  <div class="login2">
    <!-- LEFT: which portal this is -->
    <section class="brandside">
      <div class="bs-logo"><Fuel :size="20" /> Fuel Guard X</div>
      <div class="bs-portal">Driver Portal</div>
      <p class="bs-tag">Your assigned truck, live location, trips and safety alerts — right in your pocket.</p>
      <ul class="bs-list">
        <li><Check :size="16" /> Live truck location &amp; today's route</li>
        <li><Check :size="16" /> Trip history at a glance</li>
        <li><Check :size="16" /> Safety &amp; security alerts</li>
      </ul>
    </section>

    <!-- RIGHT: the login form -->
    <section class="formside">
      <div class="formcard">
        <h2>Sign in</h2>
        <p class="sub">Driver access to Fuel Guard X</p>
        <form @submit.prevent="submit">
          <label>Username</label>
          <input v-model="username" autocomplete="username" autocapitalize="none" style="margin:6px 0 14px" />
          <label>Password</label>
          <input v-model="password" type="password" autocomplete="current-password" style="margin:6px 0 18px" />
          <button class="primary" :disabled="loading">{{ loading ? 'Signing in…' : 'Sign in' }}</button>
          <div v-if="error" class="err">{{ error }}</div>
        </form>
        <p class="note">No sign-up here — driver accounts are created by your administrator.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Fuel, Check } from 'lucide-vue-next'
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

<style scoped>
.login2 { display: grid; grid-template-columns: 1.05fr .95fr; min-height: 100vh; min-height: 100dvh; }
.brandside {
  position: relative; overflow: hidden; color: #fff; background: var(--accent-grad);
  padding: 48px 46px; display: flex; flex-direction: column; justify-content: center; gap: 18px;
}
.brandside::after {
  content: ""; position: absolute; width: 460px; height: 460px; right: -140px; top: -140px;
  background: radial-gradient(circle, rgba(255,255,255,.18), transparent 70%); pointer-events: none;
}
.bs-logo { font-size: 20px; font-weight: 800; display: flex; gap: 9px; align-items: center; }
.bs-portal { font-size: 36px; font-weight: 800; letter-spacing: -.02em; line-height: 1.08; }
.bs-tag { font-size: 15px; opacity: .92; max-width: 34ch; line-height: 1.55; margin: 0; }
.bs-list { list-style: none; padding: 0; margin: 8px 0 0; display: grid; gap: 11px; }
.bs-list li { display: flex; gap: 9px; align-items: center; font-size: 14px; opacity: .96; }
.bs-list li svg { flex: none; opacity: .9; }

.formside { display: grid; place-items: center; padding: 32px 24px; background: var(--bg); }
.formcard { width: 100%; max-width: 380px; }
.formcard h2 { font-size: 23px; margin: 0 0 4px; letter-spacing: -.01em; }
.formcard .sub { color: var(--muted); margin: 0 0 22px; font-size: 14px; }
.formcard label { display: block; font-size: 12px; color: var(--muted); font-weight: 600; }
.note { margin-top: 18px; font-size: 12px; color: var(--muted); text-align: center; }

@media (max-width: 820px) {
  .login2 { grid-template-columns: 1fr; grid-template-rows: auto 1fr; }
  .brandside { padding: 26px 22px; gap: 8px; justify-content: flex-start; }
  .bs-portal { font-size: 25px; }
  .bs-tag, .bs-list { display: none; }
  .formside { padding: 28px 20px; align-items: start; }
}
</style>
