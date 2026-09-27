<!--
  Shared sign-in screen for all three portals (admin / dealer / pilot).

  Layout: desktop = navy brand panel (portal scene + value points) beside the
  form; tablet/phone = compact navy header with the form card overlapping it.
  Solid colors only (tokens from shared/design/tokens.css). The page owns the
  auth call: this component emits `submit` with the credentials and renders
  `busy` / `error` it is given.
-->
<template>
  <div class="auth" :class="`auth--${portal}`">
    <section class="auth-brand" aria-label="About this portal">
      <header class="ab-top">
        <span class="ab-logo"><img :src="logo" alt="" /></span>
        <span class="ab-name">
          <strong>Fuel Guard X</strong>
          <small>by AAYUNEX INNOVATIONS OPC Pvt Ltd.</small>
        </span>
      </header>

      <div class="ab-body">
        <p class="ab-portal"><component :is="portalIcon" :size="15" aria-hidden="true" /> {{ portalName }}</p>
        <h1 class="ab-headline">{{ headline }}</h1>
        <p class="ab-desc">{{ description }}</p>
        <div class="ab-scene"><component :is="scene" /></div>
      </div>

      <ul class="ab-points">
        <li v-for="p in points" :key="p.title">
          <span class="ab-point-ic"><component :is="p.icon" :size="18" aria-hidden="true" /></span>
          <span><strong>{{ p.title }}</strong><small>{{ p.text }}</small></span>
        </li>
      </ul>
    </section>

    <main class="auth-main">
      <div class="auth-card">
        <h2 class="ac-title">Sign in</h2>
        <p class="ac-sub">{{ formSubtitle }}</p>

        <form class="ac-form" novalidate @submit.prevent="onSubmit">
          <div class="ac-field">
            <label :for="`${portal}-username`">Username</label>
            <div class="ac-input">
              <UserRound :size="18" class="ac-ic" aria-hidden="true" />
              <input :id="`${portal}-username`" ref="userEl" v-model.trim="username" name="username"
                     autocomplete="username" autocapitalize="none" spellcheck="false" required
                     :aria-invalid="!!error" placeholder="Enter your username" />
            </div>
          </div>

          <div class="ac-field">
            <label :for="`${portal}-password`">Password</label>
            <div class="ac-input">
              <LockKeyhole :size="18" class="ac-ic" aria-hidden="true" />
              <input :id="`${portal}-password`" v-model="password" name="password"
                     :type="showPw ? 'text' : 'password'" autocomplete="current-password" required
                     :aria-invalid="!!error" placeholder="Enter your password"
                     @keyup="checkCaps" @keydown="checkCaps" />
              <button type="button" class="ac-eye" :aria-label="showPw ? 'Hide password' : 'Show password'"
                      :aria-pressed="showPw" @click="showPw = !showPw">
                <component :is="showPw ? EyeOff : Eye" :size="18" />
              </button>
            </div>
            <p v-if="capsOn" class="ac-hint"><TriangleAlert :size="14" aria-hidden="true" /> Caps Lock is on</p>
          </div>

          <p v-if="error" class="ac-error" role="alert"><CircleAlert :size="16" aria-hidden="true" /> {{ error }}</p>

          <button type="submit" class="ac-submit primary" :disabled="busy || !username || !password" :aria-busy="busy">
            <span v-if="busy" class="ac-spin" aria-hidden="true"></span>
            {{ busy ? 'Signing in…' : submitLabel }}
            <ArrowRight v-if="!busy" :size="18" aria-hidden="true" />
          </button>
        </form>

        <p class="ac-secure"><ShieldCheck :size="15" aria-hidden="true" /> {{ securityNote }}</p>
        <p class="ac-note">{{ note }}</p>
      </div>

      <footer class="auth-foot">
        <a href="https://erp.aayunexinnovations.com/"><ArrowLeft :size="14" aria-hidden="true" /> All portals</a>
        <span>© 2025 AAYUNEX INNOVATIONS OPC Pvt Ltd.</span>
      </footer>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  ArrowLeft, ArrowRight, CircleAlert, Eye, EyeOff, LockKeyhole, ShieldCheck, TriangleAlert, UserRound,
} from 'lucide-vue-next'
import brandMark from '../design/brand/aayunex-logo.png'
import AdminScene from './scenes/AdminScene.vue'
import DealerScene from './scenes/DealerScene.vue'
import PilotScene from './scenes/PilotScene.vue'

const props = defineProps({
  portal: { type: String, required: true },          // 'admin' | 'dealer' | 'pilot'
  portalName: { type: String, required: true },      // e.g. 'Admin Console'
  portalIcon: { type: [Object, Function], required: true },
  logo: { type: String, default: brandMark },         // official logo, used unaltered
  headline: { type: String, required: true },
  description: { type: String, required: true },
  points: { type: Array, default: () => [] },        // [{ icon, title, text }]
  formSubtitle: { type: String, required: true },
  submitLabel: { type: String, default: 'Sign in' },
  securityNote: { type: String, default: 'Encrypted session · signs out automatically when idle' },
  note: { type: String, default: '' },
  busy: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit'])

const scene = computed(() => ({ admin: AdminScene, dealer: DealerScene, pilot: PilotScene }[props.portal]))

const username = ref('')
const password = ref('')
const showPw = ref(false)
const capsOn = ref(false)
const userEl = ref(null)

function checkCaps(e) { capsOn.value = !!e.getModifierState?.('CapsLock') }
function onSubmit() {
  if (!username.value || !password.value || props.busy) return
  emit('submit', { username: username.value, password: password.value })
}

// Focus the first field on devices with a real keyboard (not phones, where it
// would pop the on-screen keyboard over the page).
onMounted(() => { if (matchMedia('(hover: hover) and (pointer: fine)').matches) userEl.value?.focus() })
</script>

<style scoped>
.auth {
  min-height: 100vh; min-height: 100dvh;
  display: grid; grid-template-columns: minmax(0, 1.08fr) minmax(0, 1fr);
  background: var(--bg); color: var(--text); font-family: var(--font-ui);
}

/* ---------------- brand panel ---------------- */
.auth-brand {
  background: var(--navy-900); color: #E6EDF5;
  padding: clamp(28px, 3.4vw, 52px);
  display: flex; flex-direction: column; gap: clamp(20px, 3vh, 36px);
  border-right: 1px solid var(--navy-800);
}
.ab-top { display: flex; align-items: center; gap: 12px; }
.ab-logo {
  width: 44px; height: 44px; border-radius: 10px; background: #FFFFFF;
  display: grid; place-items: center; overflow: hidden; flex: none;
}
.ab-logo img { width: 34px; height: 34px; object-fit: contain; }
.ab-name { display: flex; flex-direction: column; line-height: 1.2; }
.ab-name strong { font-size: 1.05rem; font-weight: 800; color: #FFFFFF; letter-spacing: -.01em; }
.ab-name small { font-size: .78rem; color: var(--ink-muted); }

.ab-body { flex: 1; display: flex; flex-direction: column; justify-content: center; }
.ab-portal {
  display: inline-flex; align-items: center; gap: 8px; margin: 0 0 14px;
  font-size: .74rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--flame-500);
}
.ab-headline {
  margin: 0; max-width: 20ch; color: #FFFFFF;
  font-size: clamp(1.7rem, 1.05rem + 1.9vw, 2.6rem); line-height: 1.12; font-weight: 800; letter-spacing: -.025em;
}
.ab-desc { margin: 14px 0 0; max-width: 46ch; color: #B6C3D4; font-size: 1rem; line-height: 1.6; }
.ab-scene { margin-top: clamp(20px, 3.5vh, 40px); max-width: 520px; }
.ab-scene :deep(svg) { display: block; width: 100%; height: auto; }

.ab-points {
  list-style: none; margin: 0; padding: 0;
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px;
}
.ab-points li {
  display: flex; gap: 12px; align-items: flex-start;
  padding: 14px; border-radius: 10px; background: var(--navy-800); border: 1px solid var(--navy-700);
}
.ab-point-ic {
  flex: none; width: 34px; height: 34px; border-radius: 8px; display: grid; place-items: center;
  background: var(--navy-900); color: var(--flame-500);
}
.ab-points strong { display: block; font-size: .86rem; color: #FFFFFF; font-weight: 700; }
.ab-points small { display: block; margin-top: 3px; font-size: .78rem; line-height: 1.45; color: #9FB0C5; }

/* ---------------- form side ---------------- */
.auth-main {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: clamp(24px, 4vw, 56px) clamp(16px, 4vw, 56px) 20px; gap: 22px;
}
.auth-card {
  width: 100%; max-width: 432px;
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  box-shadow: var(--shadow-md); padding: clamp(24px, 3vw, 36px);
}
.ac-title { margin: 0; font-size: 1.75rem; font-weight: 800; letter-spacing: -.02em; color: var(--text); }
.ac-sub { margin: 6px 0 24px; color: var(--muted); font-size: .95rem; line-height: 1.5; }

.ac-form { display: flex; flex-direction: column; gap: 18px; }
.ac-field label { display: block; margin-bottom: 7px; font-size: .86rem; font-weight: 600; color: var(--text); }
.ac-input { position: relative; display: flex; align-items: center; }
.ac-ic { position: absolute; left: 14px; color: var(--muted); pointer-events: none; }
.ac-input input {
  width: 100%; height: 50px; margin: 0; padding: 0 48px 0 44px;
  font: inherit; font-size: 16px; /* 16px stops iOS zooming into the field */
  color: var(--text); background: var(--field-bg);
  border: 1px solid var(--border-strong); border-radius: 10px; box-shadow: none;
  transition: border-color var(--dur) var(--ease), box-shadow var(--dur) var(--ease);
}
.ac-input input::placeholder { color: var(--muted-2); }
.ac-input input:hover { border-color: var(--muted-2); }
.ac-input input:focus { outline: none; border-color: var(--brand); box-shadow: 0 0 0 3px var(--brand-ring); }
.ac-input input[aria-invalid="true"] { border-color: var(--danger); }
.ac-eye {
  position: absolute; right: 6px; width: 38px; height: 38px; padding: 0; margin: 0;
  display: grid; place-items: center; border: 0; border-radius: 8px;
  background: transparent; color: var(--muted); cursor: pointer; box-shadow: none; transform: none;
}
.ac-eye:hover { background: var(--surface-3); color: var(--text); transform: none; }
.ac-eye:focus-visible { outline: 2px solid var(--brand); outline-offset: 1px; }
.ac-hint { display: flex; align-items: center; gap: 6px; margin: 7px 0 0; font-size: .8rem; color: var(--amber); font-weight: 600; }

.ac-error {
  display: flex; align-items: flex-start; gap: 8px; margin: 0;
  padding: 11px 13px; border-radius: 9px; font-size: .88rem; line-height: 1.4;
  background: var(--danger-soft); color: var(--danger); border: 1px solid var(--danger-ring);
}
.ac-error svg { flex: none; margin-top: 1px; }

.auth .ac-submit {
  width: 100%; height: 50px; margin: 4px 0 0; padding: 0 20px;
  display: inline-flex; align-items: center; justify-content: center; gap: 10px;
  font: inherit; font-size: 1rem; font-weight: 700; letter-spacing: .005em;
  color: #FFFFFF; background: var(--brand); border: 0; border-radius: 10px;
  box-shadow: none; filter: none; transform: none; cursor: pointer;
  transition: background-color var(--dur) var(--ease);
}
.auth .ac-submit:hover:not(:disabled) { background: var(--brand-strong); transform: none; filter: none; box-shadow: none; }
.auth .ac-submit:active:not(:disabled) { background: var(--flame-700); }
.auth .ac-submit:focus-visible { outline: 3px solid var(--brand-ring); outline-offset: 2px; }
.auth .ac-submit:disabled { background: var(--border); color: var(--muted); cursor: not-allowed; }
.auth .ac-submit[aria-busy="true"] { background: var(--brand); color: #FFFFFF; cursor: progress; }
.ac-spin {
  width: 16px; height: 16px; border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, .45); border-top-color: #FFFFFF; animation: ac-spin .7s linear infinite;
}
@keyframes ac-spin { to { transform: rotate(360deg); } }

.ac-secure {
  display: flex; align-items: center; gap: 8px; margin: 20px 0 0; padding: 10px 12px;
  border-radius: 9px; background: var(--surface-2); border: 1px solid var(--border);
  font-size: .82rem; color: var(--muted);
}
.ac-secure svg { flex: none; color: var(--green); }
.ac-note { margin: 14px 0 0; font-size: .82rem; line-height: 1.5; color: var(--muted); text-align: center; }
.ac-note:empty { display: none; }

.auth-foot {
  width: 100%; max-width: 432px; display: flex; justify-content: space-between; align-items: center; gap: 12px;
  font-size: .8rem; color: var(--muted);
}
.auth-foot a { display: inline-flex; align-items: center; gap: 6px; color: var(--muted); font-weight: 600; text-decoration: none; }
.auth-foot a:hover { color: var(--brand); }

/* ---------------- responsive ---------------- */
@media (max-width: 1240px) {
  .ab-points { grid-template-columns: 1fr; gap: 10px; }
  .ab-points li { padding: 11px 13px; }
}
@media (max-width: 960px) {
  .auth { grid-template-columns: 1fr; }
  .auth-brand {
    border-right: 0; padding: 20px 16px 84px; gap: 18px;
  }
  /* Header content lines up with the form card below it. */
  .ab-top, .ab-body { width: 100%; max-width: 432px; margin-inline: auto; }
  .ab-body { flex: none; }
  .ab-headline { font-size: clamp(1.45rem, 1.1rem + 2vw, 2rem); max-width: 22ch; }
  .ab-desc { font-size: .92rem; margin-top: 8px; }
  .ab-scene { max-width: 360px; margin: 18px auto 0; width: 100%; }
  .ab-points { display: none; }
  .auth-main { justify-content: flex-start; margin-top: -68px; padding: 0 16px 24px; }
  .auth-card { box-shadow: var(--shadow-lg); }
}
@media (max-width: 560px) {
  .ab-desc { display: none; }
  .ab-scene { max-width: 300px; }
  .ac-title { font-size: 1.5rem; }
  .auth-foot { flex-direction: column-reverse; gap: 8px; }
}
@media (max-height: 560px) and (max-width: 960px) {
  .ab-scene { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .ac-spin { animation-duration: 1.6s; }
}
</style>
