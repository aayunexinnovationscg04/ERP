<!--
  Admin console sign-in: one centred card (brand, username, password, sign in)
  on a designed full-page background. Solid colours only.
-->
<template>
  <div class="alogin">
    <FleetBackdrop />

    <main class="al-main">
      <div class="al-card">
        <div class="al-brand">
          <span class="al-logo"><img :src="logo" alt="AAYUNEX INNOVATIONS OPC Pvt Ltd. logo" /></span>
          <div class="al-brand-text">
            <strong>Fuel Guard X</strong>
            <span>AAYUNEX INNOVATIONS OPC Pvt Ltd.</span>
          </div>
        </div>

        <h1 class="al-title">Admin Console</h1>

        <form class="al-form" novalidate @submit.prevent="submit">
          <div class="al-field">
            <label for="admin-username">Username</label>
            <div class="al-input">
              <UserRound :size="18" class="al-ic" aria-hidden="true" />
              <input id="admin-username" ref="userEl" v-model.trim="username" name="username"
                     autocomplete="username" autocapitalize="none" spellcheck="false" required
                     :aria-invalid="!!error" />
            </div>
          </div>

          <div class="al-field">
            <label for="admin-password">Password</label>
            <div class="al-input">
              <LockKeyhole :size="18" class="al-ic" aria-hidden="true" />
              <input id="admin-password" v-model="password" name="password"
                     :type="showPw ? 'text' : 'password'" autocomplete="current-password" required
                     :aria-invalid="!!error" />
              <button type="button" class="al-eye" :aria-label="showPw ? 'Hide password' : 'Show password'"
                      :aria-pressed="showPw" @click="showPw = !showPw">
                <component :is="showPw ? EyeOff : Eye" :size="18" />
              </button>
            </div>
          </div>

          <p v-if="error" class="al-error" role="alert">{{ error }}</p>

          <button type="submit" class="al-submit primary" :disabled="busy || !username || !password" :aria-busy="busy">
            <span v-if="busy" class="al-spin" aria-hidden="true"></span>
            {{ busy ? 'Signing in…' : 'Sign in' }}
          </button>
        </form>
      </div>
    </main>

    <footer class="al-foot"><span>© 2025 AAYUNEX INNOVATIONS OPC Pvt Ltd.</span></footer>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Eye, EyeOff, LockKeyhole, UserRound } from 'lucide-vue-next'
import logo from '@shared/design/brand/aayunex-logo.png'
import { login, justLoggedIn } from '../auth'
import FleetBackdrop from '../components/FleetBackdrop.vue'

const username = ref('')
const password = ref('')
const showPw = ref(false)
const busy = ref(false)
const error = ref('')
const userEl = ref(null)
const router = useRouter()
const route = useRoute()

// Only follow in-app paths, never an absolute URL (open-redirect guard).
const nextPath = () => {
  const n = route.query.next
  return typeof n === 'string' && n.startsWith('/') && !n.startsWith('//') ? n : '/'
}

async function submit() {
  if (!username.value || !password.value || busy.value) return
  busy.value = true
  error.value = ''
  try {
    await login(username.value, password.value)
    justLoggedIn.value = true
    router.replace(nextPath())
  } catch (e) {
    const s = e.response?.status
    error.value = s === 429 ? 'Too many attempts. Please wait a minute and try again.'
      : s === 403 ? (e.response.data?.detail || 'This account cannot sign in here.')
        : s === 401 ? 'Incorrect username or password.'
          : 'Could not reach the server. Check your connection and try again.'
  } finally {
    busy.value = false
  }
}

onMounted(() => { if (matchMedia('(hover: hover) and (pointer: fine)').matches) userEl.value?.focus() })
</script>

<style scoped>
.alogin {
  position: relative; min-height: 100vh; min-height: 100dvh; overflow: hidden;
  display: flex; flex-direction: column; background: var(--navy-900); font-family: var(--font-ui);
}

.al-main {
  position: relative; flex: 1; display: flex; align-items: center; justify-content: center;
  padding: 24px 16px;
}
.al-card {
  width: 100%; max-width: 400px; padding: 32px;
  background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, .35);
}

.al-brand { display: flex; align-items: center; gap: 14px; }
.al-logo {
  flex: none; width: 60px; height: 60px; border-radius: 14px; background: #FFFFFF;
  border: 1px solid #E2E8F0; display: grid; place-items: center;
}
.al-logo img { width: 54px; height: 54px; object-fit: contain; }
.al-brand-text { display: flex; flex-direction: column; min-width: 0; line-height: 1.25; }
.al-brand-text strong { font-size: 1.15rem; font-weight: 800; color: var(--text); letter-spacing: -.01em; }
.al-brand-text span { font-size: .78rem; color: var(--muted); }

.al-title {
  margin: 24px 0 20px; padding-top: 20px; border-top: 1px solid var(--border);
  font-size: 1.5rem; font-weight: 800; letter-spacing: -.02em; color: var(--text);
}

.al-form { display: flex; flex-direction: column; gap: 16px; }
.al-field label { display: block; margin-bottom: 7px; font-size: .86rem; font-weight: 600; color: var(--text); }
.al-input { position: relative; display: flex; align-items: center; }
.al-ic { position: absolute; left: 14px; color: var(--muted); pointer-events: none; }
.al-input input {
  width: 100%; height: 48px; margin: 0; padding: 0 48px 0 44px;
  font: inherit; font-size: 16px; color: var(--text); background: var(--field-bg);
  border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: none;
  transition: border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease);
}
.al-input input:hover { border-color: var(--muted-2); }
.al-input input:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 3px var(--brand-ring); }
.al-input input[aria-invalid="true"] { border-color: var(--danger); }
.al-eye {
  position: absolute; right: 5px; width: 38px; height: 38px; padding: 0; margin: 0;
  display: grid; place-items: center; border: 0; border-radius: 8px;
  background: transparent; color: var(--muted); cursor: pointer; box-shadow: none; transform: none;
}
.al-eye:hover { background: var(--surface-3); color: var(--text); transform: none; }
.al-eye:focus-visible { outline: 2px solid var(--brand); outline-offset: 1px; }

.al-error {
  margin: 0; padding: 10px 12px; border-radius: 9px; font-size: .88rem;
  background: var(--danger-soft); color: var(--danger); border: 1px solid var(--danger-ring);
}

.alogin .al-submit {
  width: 100%; height: 48px; margin: 6px 0 0; padding: 0 20px;
  display: inline-flex; align-items: center; justify-content: center; gap: 10px;
  font: inherit; font-size: 1rem; font-weight: 700; color: #FFFFFF;
  background: var(--brand); border: 0; border-radius: 10px;
  box-shadow: none; filter: none; transform: none; cursor: pointer;
  transition: background-color var(--dur) var(--ease);
}
.alogin .al-submit:hover:not(:disabled) { background: var(--brand-strong); transform: none; filter: none; box-shadow: none; }
.alogin .al-submit:focus-visible { outline: 3px solid var(--brand-ring); outline-offset: 2px; }
.alogin .al-submit:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; }
.alogin .al-submit[aria-busy="true"] { background: var(--brand); color: #FFFFFF; cursor: progress; }
.al-spin {
  width: 16px; height: 16px; border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, .45); border-top-color: #FFFFFF; animation: al-spin .7s linear infinite;
}
@keyframes al-spin { to { transform: rotate(360deg); } }

.al-foot {
  position: relative; padding: 0 16px 16px; text-align: center; font-size: .8rem; color: #B6C3D4;
}
.al-foot span { display: inline-block; padding: 5px 12px; border-radius: 8px; background: #0B1F33; border: 1px solid #1B3A5C; }

@media (max-width: 480px) {
  .al-card { padding: 24px 20px; border-radius: 14px; }
  .al-title { margin: 20px 0 16px; padding-top: 16px; font-size: 1.35rem; }
}
</style>
