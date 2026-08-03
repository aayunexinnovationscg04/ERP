<template>
  <div class="login2">
    <!-- LEFT: which portal this is -->
    <section class="brandside">
      <ParticleField class="bs-particles" />
      <div class="bs-pattern" aria-hidden="true"></div>
      <div class="bs-content">
        <div class="bs-logo"><span class="bs-logo-badge"><img src="../assets/logo.png" alt="" /></span> Fuel Guard X</div>
        <div class="bs-portal">Admin Console</div>
        <p class="bs-tag">Manage companies, users, roles and tab-level access across the platform.</p>
        <ul class="bs-list">
          <li><span class="bs-ic"><Check :size="13" /></span> User &amp; company management</li>
          <li><span class="bs-ic"><Check :size="13" /></span> Role-based access control</li>
          <li><span class="bs-ic"><Check :size="13" /></span> Per-member permission overrides</li>
        </ul>
        <div class="bs-live"><span class="live-dot"></span> Platform-wide oversight</div>
      </div>
    </section>

    <!-- RIGHT: the login form -->
    <section class="formside">
      <div class="formcard">
        <div class="form-badge"><img src="../assets/logo.png" alt="" style="width:24px;height:24px;object-fit:cover;border-radius:6px" /></div>
        <h2>Sign in</h2>
        <p class="sub">Platform administration — authorized staff only</p>
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
          <button class="primary" :disabled="busy">{{ busy ? 'Signing in…' : 'Sign in' }}</button>
          <div v-if="error" class="err">{{ error }}</div>
        </form>
        <p class="note">No sign-up — admin accounts are provisioned internally.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Check, User, Lock, Eye, EyeOff } from 'lucide-vue-next'
import { login } from '../api'
import { setAuth } from '../auth'
import { toast } from '../toast'
import ParticleField from '../components/ParticleField.vue'

const username = ref(''); const password = ref(''); const busy = ref(false); const error = ref('')
const showPw = ref(false)
const router = useRouter()
async function submit() {
  busy.value = true; error.value = ''
  try {
    const data = await login(username.value, password.value)
    if (data.user?.role !== 'admin') {
      error.value = 'Not an admin account.'
      toast.error('Not an admin account')
      return
    }
    setAuth({ access: data.access, refresh: data.refresh, user: data.user })
    router.push('/users')
  } catch (e) {
    error.value = e.response?.status === 429
      ? 'Too many attempts. Please wait a minute and try again.'
      : (e.response?.status === 401 ? 'Invalid username or password.' : 'Login failed.')
    toast.error(error.value)
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
    radial-gradient(circle, rgba(255,255,255,.14) 1.5px, transparent 1.5px);
  background-size: 26px 26px;
  -webkit-mask-image: radial-gradient(120% 90% at 15% 20%, #000 0%, transparent 72%);
          mask-image: radial-gradient(120% 90% at 15% 20%, #000 0%, transparent 72%);
}
.brandside::after {
  content: ""; position: absolute; width: 460px; height: 460px; right: -160px; top: -160px;
  background: radial-gradient(circle, rgba(255,255,255,.12), transparent 70%); pointer-events: none;
}
.brandside::before {
  content: ""; position: absolute; width: 360px; height: 360px; left: -120px; bottom: -140px;
  background: radial-gradient(circle, rgba(0,0,0,.22), transparent 72%); pointer-events: none;
}
.bs-content { position: relative; z-index: 1; display: flex; flex-direction: column; gap: 18px; }
.bs-logo { font-size: 15px; font-weight: 700; display: flex; gap: 10px; align-items: center; opacity: .92; }
.bs-logo-badge {
  width: 30px; height: 30px; border-radius: 9px; display: grid; place-items: center; flex: none;
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.2); overflow: hidden;
}
.bs-logo-badge img { width: 100%; height: 100%; object-fit: cover; }
.bs-particles { position: absolute; inset: 0; z-index: 0; opacity: .8; }
.bs-portal { font-size: 34px; font-weight: 850; letter-spacing: -.03em; line-height: 1.08; }
.bs-tag { font-size: 15px; opacity: .9; max-width: 34ch; line-height: 1.55; margin: 0; }
.bs-list { list-style: none; padding: 0; margin: 4px 0 0; display: grid; gap: 12px; }
.bs-list li { display: flex; gap: 10px; align-items: center; font-size: 14px; opacity: .94; }
.bs-ic {
  width: 20px; height: 20px; border-radius: 6px; flex: none; display: grid; place-items: center;
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.2);
}
.bs-live {
  margin-top: 8px; display: inline-flex; align-items: center; gap: 8px; width: fit-content;
  font-size: 12.5px; font-weight: 700; padding: 7px 13px; border-radius: 999px;
  background: rgba(255,255,255,.1); border: 1px solid rgba(255,255,255,.18); opacity: .96;
}
.bs-live .live-dot {
  width: 9px; height: 9px; border-radius: 50%; flex: none;
  background: #fff; box-shadow: 0 0 0 0 rgba(255,255,255,.5);
  animation: bs-pulse 1.8s cubic-bezier(.4,0,.2,1) infinite;
}
@keyframes bs-pulse {
  0% { box-shadow: 0 0 0 0 rgba(255,255,255,.45); }
  70% { box-shadow: 0 0 0 10px rgba(255,255,255,0); }
  100% { box-shadow: 0 0 0 0 rgba(255,255,255,0); }
}

.formside { display: grid; place-items: center; padding: 32px 24px; background: var(--bg); }
.formcard { width: 100%; max-width: 380px; }
.form-badge {
  width: 46px; height: 46px; border-radius: 13px; display: none; place-items: center;
  background: var(--accent-grad); color: #fff; box-shadow: var(--shadow-brand); margin-bottom: 16px;
}
.formcard h2 { font-size: 23px; margin: 0 0 4px; letter-spacing: -.01em; }
.formcard .sub { color: var(--muted); margin: 0 0 24px; font-size: 14px; }
.formcard label { display: block; font-size: 12px; color: var(--muted); font-weight: 600; margin: 0 0 6px; }
.formcard label:not(:first-of-type) { margin-top: 16px; }
.note { margin-top: 18px; font-size: 12px; color: var(--muted); text-align: center; }

.field { position: relative; display: flex; align-items: center; }
.field-ic { position: absolute; left: 14px; color: var(--muted); pointer-events: none; z-index: 1; }
.field input { padding-left: 40px; padding-right: 40px; }
.field-toggle {
  position: absolute; right: 5px; width: 32px; height: 32px; padding: 0; border: none;
  background: transparent; color: var(--muted); display: grid; place-items: center; border-radius: 8px;
}
.field-toggle:hover { background: var(--surface-2); color: var(--text); }
.field-toggle:active { transform: scale(.94); }

@media (max-width: 820px) {
  .login2 { grid-template-columns: 1fr; grid-template-rows: auto 1fr; }
  .brandside {
    padding: 34px 24px 46px; min-height: 0;
    border-radius: 0 0 28px 28px;
  }
  .bs-content { gap: 10px; }
  .bs-portal { font-size: 24px; }
  .bs-tag { font-size: 13.5px; max-width: 42ch; opacity: .95; }
  .bs-list { display: none; }
  .bs-live { display: none; }
  .formside { padding: 0 22px; align-items: flex-start; }
  .formcard { margin-top: -26px; background: var(--surface); border: 1px solid var(--border);
    border-radius: 20px; padding: 26px 22px 24px; box-shadow: var(--shadow-md); position: relative; z-index: 2; }
  .form-badge { display: grid; }
}
</style>
