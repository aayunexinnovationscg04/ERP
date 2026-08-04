<template>
  <div class="wgate" role="status" aria-live="polite">
    <motion.div class="wgate-panel wgate-left"
      :initial="{ x: 0 }" :animate="{ x: opening ? '-100%' : 0 }"
      :transition="{ duration: reduced ? 0 : .55, ease: [.65, 0, .35, 1] }" />
    <motion.div class="wgate-panel wgate-right"
      :initial="{ x: 0 }" :animate="{ x: opening ? '100%' : 0 }"
      :transition="{ duration: reduced ? 0 : .55, ease: [.65, 0, .35, 1] }" />
    <motion.div class="wgate-content"
      :initial="{ opacity: 0, y: reduced ? 0 : 12 }" :animate="{ opacity: opening ? 0 : 1, y: opening ? (reduced ? 0 : -8) : 0 }"
      :transition="{ duration: reduced ? 0 : (opening ? .28 : .45), ease: [.4, 0, .2, 1] }">
      <span class="wgate-logo"><img :src="logo" alt="" /></span>
      <div class="wgate-brand">AAYUNEX INNOVATIONS</div>
      <div class="wgate-welcome">Welcome, {{ name }}</div>
      <div class="wgate-loader" aria-hidden="true"><span></span></div>
    </motion.div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { motion } from 'motion-v'
import logo from '../assets/logo.png'

// Entrance transition shown once, right after a successful sign-in: masks
// the ~1.5s it takes the destination page's own data to load behind a
// branded "gate" instead of a blank shell / loading skeleton flash. The
// route navigation already happened by the time this mounts (App.vue
// renders it as an overlay on top of the dashboard), so the target page is
// loading its own data concurrently, underneath this.
const { name } = defineProps({ name: { type: String, default: 'back' } })
const emit = defineEmits(['done'])

const reduced = typeof window !== 'undefined' && window.matchMedia
  ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
  : false
const opening = ref(false)
const HOLD_MS = 1500 // gate opens at the 1.5s mark, per the intended feel
const OPEN_MS = reduced ? 0 : 550 // matches the panel transition duration above

onMounted(() => {
  const t = setTimeout(() => { opening.value = true }, HOLD_MS)
  const t2 = setTimeout(() => { emit('done') }, HOLD_MS + OPEN_MS)
  return () => { clearTimeout(t); clearTimeout(t2) }
})
</script>

<style scoped>
.wgate { position: fixed; inset: 0; z-index: 900; pointer-events: none; }
.wgate-panel {
  position: absolute; top: 0; bottom: 0; width: 50%;
  background: var(--accent-grad);
}
.wgate-left { left: 0; }
.wgate-right { right: 0; }
.wgate-content {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 10px; color: #fff; text-align: center;
}
.wgate-logo {
  width: 56px; height: 56px; border-radius: 15px; display: grid; place-items: center;
  background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.24); margin-bottom: 6px;
}
.wgate-logo img { width: 34px; height: 34px; object-fit: contain; }
.wgate-brand { font-size: 13px; font-weight: 800; letter-spacing: .1em; opacity: .88; }
.wgate-welcome { font-size: clamp(24px, 4vw, 34px); font-weight: 850; letter-spacing: -.02em; }
.wgate-loader { margin-top: 14px; width: 84px; height: 3px; border-radius: 999px; background: rgba(255,255,255,.22); overflow: hidden; }
.wgate-loader span {
  display: block; width: 40%; height: 100%; border-radius: 999px; background: #fff;
  animation: wgate-sweep 1.1s cubic-bezier(.4,0,.2,1) infinite;
}
@keyframes wgate-sweep {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(250%); }
}
@media (prefers-reduced-motion: reduce) {
  .wgate-loader span { animation: none; width: 100%; }
}
</style>
