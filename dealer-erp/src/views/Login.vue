<template>
  <div class="login2">
    <!-- LEFT: which portal this is -->
    <section class="brandside">
      <AmbientOrb />
      <div class="bs-pattern" aria-hidden="true"></div>
      <motion.div class="bs-content"
        :initial="{ opacity: 0, y: 14 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: .45, ease: [.4, 0, .2, 1] }">
        <div class="bs-logo">
          <span class="bs-logo-badge"><img :src="logo" alt="" /></span>
          <span class="bs-logo-text"><strong>AAYUNEX INNOVATIONS</strong></span>
        </div>
        <div class="bs-portal">Dealer Portal</div>
        <p class="bs-tag">Track your whole fleet — vehicles, fuel, pilots and alerts — in real time.</p>
        <ul class="bs-list">
          <motion.li v-for="(f, i) in features" :key="f.text"
            :initial="{ opacity: 0, x: -10 }" :animate="{ opacity: 1, x: 0 }"
            :transition="{ duration: .35, delay: .15 + i * .08, ease: [.4, 0, .2, 1] }">
            <span class="bs-ic"><Check :size="13" /></span> {{ f.text }}
          </motion.li>
        </ul>
        <div class="bs-live"><span class="live-dot"></span> Live tracking, always on</div>
      </motion.div>
    </section>

    <!-- RIGHT: the login form -->
    <section class="formside">
      <motion.div class="formcard"
        :initial="{ opacity: 0, y: 10 }" :animate="{ opacity: 1, y: 0 }" :transition="{ duration: .4, delay: .1, ease: [.4, 0, .2, 1] }">
        <div class="form-badge"><img :src="logo" alt="" /></div>
        <h2>Sign in</h2>
        <p class="sub">Dealer / company access to Aayunex Innovations</p>
        <form @submit.prevent="submit">
          <label>Username</label>
          <div class="field">
            <User :size="16" class="field-ic" />
            <input v-model="username" autocomplete="username" autocapitalize="none" />
          </div>
          <label>Password</label>
          <div class="field">
            <Lock :size="16" class="field-ic" />
            <input v-model="password" :type="showPw ? 'text' : 'password'" autocomplete="current-password" />
            <button type="button" class="field-toggle" tabindex="-1" @click="showPw = !showPw" :aria-label="showPw ? 'Hide password' : 'Show password'">
              <component :is="showPw ? EyeOff : Eye" :size="16" />
            </button>
          </div>
          <motion.button class="primary" :disabled="busy" :while-tap="{ scale: .97 }" :while-hover="{ y: -1 }">
            {{ busy ? 'Signing in…' : 'Sign in' }}
          </motion.button>
          <div v-if="error" class="err">{{ error }}</div>
        </form>
      </motion.div>
    </section>
  </div>
</template>

<script setup>
import { defineAsyncComponent, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Check, User, Lock, Eye, EyeOff } from 'lucide-vue-next'
import { motion } from 'motion-v'
import { login } from '../api'
import { setAuth, justLoggedIn } from '../auth'
import logo from '../assets/logo.png'

// three.js is a heavy dependency (~150-600kB depending on tree-shaking) that
// only this one ambient accent needs — code-split it into its own chunk so
// it's fetched lazily on the login route instead of bloating the shared app
// bundle every other screen has to download and parse first.
const AmbientOrb = defineAsyncComponent(() => import('../components/AmbientOrb.vue'))

const features = [
  { text: 'Live fleet map & vehicle status' },
  { text: 'Fuel, trips & route history' },
  { text: 'Overspeed, geofence & tamper alerts' },
]

const username = ref('')
const password = ref('')
const busy = ref(false)
const error = ref('')
const showPw = ref(false)
const router = useRouter()

async function submit() {
  busy.value = true; error.value = ''
  try {
    const data = await login(username.value, password.value)
    setAuth({ access: data.access, refresh: data.refresh, user: data.user })
    justLoggedIn.value = true
    router.push('/')
  } catch (e) {
    error.value = e.response?.status === 429
      ? 'Too many attempts. Please wait a minute and try again.'
      : (e.response?.status === 401 ? 'Invalid username or password.' : 'Login failed.')
  } finally { busy.value = false }
}
</script>

<style scoped>
.login2 { display: grid; grid-template-columns: 1.05fr .95fr; min-height: 100vh; min-height: 100dvh; }

.brandside {
  position: relative; overflow: hidden; color: #fff; background: var(--accent-grad);
  padding: 48px 46px; display: flex; flex-direction: column; justify-content: center;
}
.bs-pattern {
  position: absolute; inset: 0; pointer-events: none;
  background-image:
    radial-gradient(circle, rgba(255,255,255,.16) 1.5px, transparent 1.5px);
  background-size: 26px 26px;
  -webkit-mask-image: radial-gradient(120% 90% at 15% 20%, #000 0%, transparent 72%);
          mask-image: radial-gradient(120% 90% at 15% 20%, #000 0%, transparent 72%);
}
.brandside::after {
  content: ""; position: absolute; width: 460px; height: 460px; right: -160px; top: -160px;
  background: radial-gradient(circle, rgba(255,255,255,.20), transparent 70%); pointer-events: none;
}
.brandside::before {
  content: ""; position: absolute; width: 360px; height: 360px; left: -120px; bottom: -140px;
  background: radial-gradient(circle, rgba(0,0,0,.14), transparent 72%); pointer-events: none;
}
.bs-content { position: relative; z-index: 1; display: flex; flex-direction: column; gap: 18px; }
.bs-logo { font-size: 15px; font-weight: 700; display: flex; gap: 10px; align-items: center; opacity: .96; }
.bs-logo-badge {
  width: 34px; height: 34px; border-radius: 9px; display: grid; place-items: center; flex: none;
  background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.22);
}
.bs-logo-badge img { width: 22px; height: 22px; object-fit: contain; }
.bs-logo-text { display: flex; flex-direction: column; gap: 2px; line-height: 1.15; }
.bs-logo-text strong { font-size: 14px; font-weight: 800; letter-spacing: .03em; }
.bs-logo-text small { font-size: 11.5px; font-weight: 500; opacity: .85; letter-spacing: .01em; }
.bs-portal { font-size: 38px; font-weight: 850; letter-spacing: -.03em; line-height: 1.08; }
.bs-tag { font-size: 15px; opacity: .92; max-width: 34ch; line-height: 1.55; margin: 0; }
.bs-list { list-style: none; padding: 0; margin: 4px 0 0; display: grid; gap: 12px; }
.bs-list li { display: flex; gap: 10px; align-items: center; font-size: 14px; opacity: .97; }
.bs-ic {
  width: 20px; height: 20px; border-radius: 6px; flex: none; display: grid; place-items: center;
  background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.2);
}
.bs-live {
  margin-top: 8px; display: inline-flex; align-items: center; gap: 8px; width: fit-content;
  font-size: 12.5px; font-weight: 700; padding: 7px 13px; border-radius: 999px;
  background: rgba(255,255,255,.14); border: 1px solid rgba(255,255,255,.2); opacity: .96;
}
.bs-live .live-dot { background: #fff; box-shadow: 0 0 0 0 rgba(255,255,255,.5); }

.formside { display: grid; place-items: center; padding: 32px 24px; background: var(--bg); }
.formcard { width: 100%; max-width: 380px; }
.form-badge {
  width: 46px; height: 46px; border-radius: 13px; display: none; place-items: center;
  background: var(--accent-grad); color: #fff; box-shadow: var(--shadow-brand); margin-bottom: 16px;
}
.form-badge img { width: 28px; height: 28px; object-fit: contain; }
.formcard h2 { font-size: 23px; margin: 0 0 4px; letter-spacing: -.01em; }
.formcard .sub { color: var(--muted); margin: 0 0 24px; font-size: 14px; }
.formcard label { display: block; font-size: 12px; color: var(--muted); font-weight: 600; margin: 0 0 6px; }
.formcard label:not(:first-of-type) { margin-top: 16px; }

.field { position: relative; display: flex; align-items: center; }
.field-ic { position: absolute; left: 14px; color: var(--muted); pointer-events: none; z-index: 1; }
.field input { padding-left: 40px; padding-right: 40px; }
.field-toggle {
  position: absolute; right: 5px; width: 32px; height: 32px; padding: 0; border: none;
  background: transparent; color: var(--muted); display: grid; place-items: center; border-radius: 8px;
}
.field-toggle:hover { background: var(--surface-2); color: var(--text); }
.field-toggle:active { transform: scale(.94); }

.formcard form button.primary {
  width: 100%; margin-top: 20px; display: flex; align-items: center; justify-content: center;
}

@media (max-width: 820px) {
  .login2 { grid-template-columns: 1fr; grid-template-rows: auto 1fr; }
  /* min-height (not the old 0) so the hero absorbs the extra vertical space
     on tall phones by growing, instead of leaving it as dead black space
     below the card — .brandside is already justify-content:center from the
     base rule, so its content stays vertically centered as it grows. */
  .brandside {
    padding: 26px 24px 30px; min-height: 38dvh;
    border-radius: 0 0 28px 28px;
  }
  .bs-content { gap: 10px; }
  .bs-portal { font-size: 26px; }
  .bs-tag { font-size: 13.5px; max-width: 42ch; opacity: .95; }
  .bs-list { display: none; }
  .bs-live { display: none; }
  .formside { padding: 0 22px 28px; align-items: flex-start; }
  .formcard { margin-top: -26px; background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; padding: 26px 22px 24px; box-shadow: var(--shadow-md); position: relative; z-index: 2; }
  .form-badge { display: grid; }
}
</style>
