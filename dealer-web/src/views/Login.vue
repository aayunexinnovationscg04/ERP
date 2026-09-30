<!--
  Dealer portal sign-in: one centred card (brand, username, password, sign in)
  on a designed full-page background. Solid colours only.
-->
<template>
  <div class="alogin">
    <FleetBackdrop />

    <main class="al-main">
      <div class="al-card">
        <header class="al-head">
          <div class="al-brand">
            <span class="al-logo"><img :src="logo" alt="AAYUNEX INNOVATIONS OPC Pvt Ltd. logo" /></span>
            <div class="al-brand-text">
              <strong>Fuel Guard X</strong>
              <span>AAYUNEX INNOVATIONS OPC Pvt Ltd.</span>
            </div>
          </div>
          <h1 class="al-title"><Truck :size="15" aria-hidden="true" /> Dealer Portal</h1>
        </header>

        <form class="al-form" novalidate @submit.prevent="submit">
          <div class="al-field">
            <label for="dealer-username">Username</label>
            <div class="al-input">
              <UserRound :size="18" class="al-ic" aria-hidden="true" />
              <input id="dealer-username" ref="userEl" v-model.trim="username" name="username"
                     autocomplete="username" autocapitalize="none" spellcheck="false" required
                     :aria-invalid="!!error" />
            </div>
          </div>

          <div class="al-field">
            <label for="dealer-password">Password</label>
            <div class="al-input">
              <LockKeyhole :size="18" class="al-ic" aria-hidden="true" />
              <input id="dealer-password" v-model="password" name="password"
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
            <ArrowRight v-if="!busy" :size="17" aria-hidden="true" />
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
import { ArrowRight, Eye, EyeOff, LockKeyhole, Truck, UserRound } from 'lucide-vue-next'
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
  width: 100%; max-width: 360px; overflow: hidden;
  background: var(--surface); border: 1px solid #1F3A5A; border-radius: 14px;
  border-top: 4px solid var(--flame-600);
  box-shadow: 0 24px 48px rgba(0, 0, 0, .35);
}

/* navy header band: brand + portal badge */
.al-head { padding: 20px 22px 18px; background: var(--navy-800); border-bottom: 1px solid #1F3A5A; }
.al-brand { display: flex; align-items: center; gap: 12px; }
.al-logo {
  flex: none; width: 52px; height: 52px; border-radius: 12px; background: #FFFFFF;
  display: grid; place-items: center;
}
.al-logo img { width: 46px; height: 46px; object-fit: contain; }
.al-brand-text { display: flex; flex-direction: column; min-width: 0; line-height: 1.25; }
.al-brand-text strong { font-size: 1.05rem; font-weight: 800; color: #FFFFFF; letter-spacing: -.01em; }
.al-brand-text span { font-size: .74rem; color: #94A6BD; }
.al-title {
  display: inline-flex; align-items: center; gap: 7px; margin: 16px 0 0; padding: 6px 11px;
  border-radius: 999px; background: var(--navy-900); border: 1px solid #264B73;
  font-size: .78rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--flame-500);
}

.al-form { display: flex; flex-direction: column; gap: 14px; padding: 22px; }
.al-field label { display: block; margin-bottom: 6px; font-size: .82rem; font-weight: 600; color: var(--text); }
.al-input { position: relative; display: flex; align-items: center; }
.al-ic { position: absolute; left: 13px; color: var(--muted); pointer-events: none; }
.al-input input {
  width: 100%; height: 44px; margin: 0; padding: 0 46px 0 42px;
  font: inherit; font-size: 16px; color: var(--text); background: var(--field-bg);
  border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: none;
  transition: border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease);
}
.al-input input:hover { border-color: var(--muted-2); }
.al-input input:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 3px var(--brand-ring); }
.al-input input[aria-invalid="true"] { border-color: var(--danger); }
.al-eye {
  position: absolute; right: 4px; width: 36px; height: 36px; min-height: 0; padding: 0; margin: 0;
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
  width: 100%; height: 44px; margin: 4px 0 0; padding: 0 18px;
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  font: inherit; font-size: .95rem; font-weight: 700; color: #FFFFFF;
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
  .al-head { padding: 18px 18px 16px; }
  .al-form { padding: 18px; }
}
</style>
