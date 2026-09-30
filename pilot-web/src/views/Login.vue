<!--
  Pilot App sign-in: split screen — form on the left, artwork on the right.
  Each portal has its own artwork (components/LoginArt.vue); on phones the
  artwork becomes a short band above the form. Solid colours only.
-->
<template>
  <div class="slogin" :class="'form-left'">
    <section class="sl-art" aria-hidden="true">
      <div class="sl-art-img"><LoginArt /></div>
      <div class="sl-caption">
        <p>Your truck, your route, your trips.</p>
      </div>
    </section>

    <div class="sl-side">
      <main class="sl-main">
        <div class="sl-panel">
          <div class="al-brand">
            <span class="al-logo"><img :src="logo" alt="AAYUNEX INNOVATIONS OPC Pvt Ltd. logo" /></span>
            <div class="al-brand-text">
              <strong>Fuel Guard X</strong>
              <span>AAYUNEX INNOVATIONS OPC Pvt Ltd.</span>
            </div>
          </div>
          <h1 class="al-title"><Navigation :size="15" aria-hidden="true" /> Pilot App</h1>
          <form class="al-form" novalidate @submit.prevent="submit">
          <div class="al-field">
            <label for="pilot-username">Username</label>
            <div class="al-input">
              <UserRound :size="18" class="al-ic" aria-hidden="true" />
              <input id="pilot-username" ref="userEl" v-model.trim="username" name="username"
                     autocomplete="username" autocapitalize="none" spellcheck="false" required
                     :aria-invalid="!!error" />
            </div>
          </div>

          <div class="al-field">
            <label for="pilot-password">Password</label>
            <div class="al-input">
              <LockKeyhole :size="18" class="al-ic" aria-hidden="true" />
              <input id="pilot-password" v-model="password" name="password"
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
      <footer class="al-foot">© 2025 AAYUNEX INNOVATIONS OPC Pvt Ltd.</footer>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, Eye, EyeOff, LockKeyhole, Navigation, UserRound } from 'lucide-vue-next'
import logo from '@shared/design/brand/aayunex-logo.png'
import { login, justLoggedIn } from '../auth'
import LoginArt from '../components/LoginArt.vue'

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
.slogin {
  min-height: 100vh; min-height: 100dvh; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  grid-template-areas: "art side"; background: var(--bg); font-family: var(--font-ui);
}
.slogin.form-left { grid-template-areas: "side art"; }

/* artwork half */
.sl-art { grid-area: art; display: flex; flex-direction: column; overflow: hidden; background: var(--navy-900); min-height: 100%; }
.sl-art-img { position: relative; flex: 1; min-height: 0; }
.sl-caption { flex: none; padding: 22px 40px 28px; background: var(--navy-900); border-top: 1px solid var(--navy-700); }
.sl-caption p { margin: 0; font-size: 1.35rem; font-weight: 750; line-height: 1.3; color: #FFFFFF; letter-spacing: -.01em; }

/* form half */
.sl-side { grid-area: side; display: flex; flex-direction: column; min-width: 0; }
.sl-main { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 24px; }
.sl-panel { width: 100%; max-width: 380px; }

.al-brand { display: flex; align-items: center; gap: 12px; }
.al-logo {
  flex: none; width: 56px; height: 56px; border-radius: 14px; background: #FFFFFF;
  border: 1px solid var(--border); display: grid; place-items: center;
}
.al-logo img { width: 48px; height: 48px; object-fit: contain; }
.al-brand-text { display: flex; flex-direction: column; min-width: 0; line-height: 1.25; }
.al-brand-text strong { font-size: 1.15rem; font-weight: 800; color: var(--ink-strong); letter-spacing: -.01em; }
.al-brand-text span { font-size: .76rem; color: var(--muted); }
.al-title {
  display: inline-flex; align-items: center; gap: 7px; margin: 20px 0 6px; padding: 6px 11px;
  border-radius: 999px; background: var(--brand-soft); border: 1px solid var(--brand-ring);
  font-size: .78rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--brand-soft-ink, var(--brand));
}

.al-form { display: flex; flex-direction: column; gap: 14px; margin-top: 18px; }
.al-field label { display: block; margin-bottom: 6px; font-size: .82rem; font-weight: 600; color: var(--text); }
.al-input { position: relative; display: flex; align-items: center; }
.al-ic { position: absolute; left: 13px; color: var(--muted); pointer-events: none; }
.al-input input {
  width: 100%; height: 46px; margin: 0; padding: 0 46px 0 42px;
  font: inherit; font-size: 16px; color: var(--text); background: var(--field-bg);
  border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: none;
  transition: border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease);
}
.al-input input:hover { border-color: var(--muted-2); }
.al-input input:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 3px var(--brand-ring); }
.al-input input[aria-invalid="true"] { border-color: var(--danger); }
.al-eye {
  position: absolute; right: 4px; width: 38px; height: 38px; min-height: 0; padding: 0; margin: 0;
  display: grid; place-items: center; border: 0; border-radius: 8px;
  background: transparent; color: var(--muted); cursor: pointer; box-shadow: none; transform: none;
}
.al-eye:hover { background: var(--surface-3); color: var(--text); transform: none; }
.al-eye:focus-visible { outline: 2px solid var(--brand); outline-offset: 1px; }
.al-error {
  margin: 0; padding: 10px 12px; border-radius: 9px; font-size: .88rem;
  background: var(--danger-soft); color: var(--danger); border: 1px solid var(--danger-ring);
}
.slogin .al-submit {
  width: 100%; height: 46px; margin: 4px 0 0; padding: 0 18px;
  display: inline-flex; align-items: center; justify-content: center; gap: 8px;
  font: inherit; font-size: .95rem; font-weight: 700; color: #FFFFFF;
  background: var(--brand); border: 0; border-radius: 10px;
  box-shadow: none; filter: none; transform: none; cursor: pointer;
  transition: background-color var(--dur) var(--ease);
}
.slogin .al-submit:hover:not(:disabled) { background: var(--brand-strong); transform: none; filter: none; box-shadow: none; }
.slogin .al-submit:focus-visible { outline: 3px solid var(--brand-ring); outline-offset: 2px; }
.slogin .al-submit:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; }
.slogin .al-submit[aria-busy="true"] { background: var(--brand); color: #FFFFFF; cursor: progress; }
.al-spin {
  width: 16px; height: 16px; border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, .45); border-top-color: #FFFFFF; animation: al-spin .7s linear infinite;
}
@keyframes al-spin { to { transform: rotate(360deg); } }
.al-foot { padding: 0 24px 20px; text-align: center; font-size: .78rem; color: var(--muted); }

/* tablets/phones: artwork becomes a short band above the form */
@media (max-width: 900px) {
  .slogin, .slogin.form-left { grid-template-columns: minmax(0, 1fr); grid-template-rows: auto 1fr; grid-template-areas: "art" "side"; }
  .sl-art { height: 210px; min-height: 0; }
  .sl-art-img { height: 100%; }
  .sl-caption { display: none; }
  .sl-main { align-items: flex-start; padding: 24px 16px 28px; }
}
@media (max-width: 380px) { .sl-art { height: 170px; } }
@media (max-height: 560px) and (max-width: 900px) { .sl-art { display: none; } .slogin { grid-template-areas: "side"; } }
</style>
