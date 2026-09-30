// Small shared motion helpers built on top of motion-v (the Vue port of the
// Motion One engine — the closest legitimate equivalent to Framer Motion for
// Vue 3). Kept tiny and centralized so every view respects
// `prefers-reduced-motion` the same way, and so easing/duration stay in sync
// with the CSS tokens in style.css (--ease / --dur).
import { ref, onMounted, onBeforeUnmount } from 'vue'

export const EASE = [0.4, 0, 0.2, 1]

export function usePrefersReducedMotion() {
  const reduced = ref(false)
  let mq
  function update() { reduced.value = mq.matches }
  onMounted(() => {
    if (!window.matchMedia) return
    mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    update()
    mq.addEventListener ? mq.addEventListener('change', update) : mq.addListener(update)
  })
  onBeforeUnmount(() => {
    if (!mq) return
    mq.removeEventListener ? mq.removeEventListener('change', update) : mq.removeListener(update)
  })
  return reduced
}

// A page-enter transition preset. Pass the reduced-motion ref to zero it out.
export function pageTransition(reduced) {
  return reduced?.value
    ? { duration: 0 }
    : { duration: 0.24, ease: EASE }
}

// A short, tasteful "emphasis" transition for status changes (trip start/end,
// a new alert appearing) — snappy, not bouncy.
export function emphasisTransition(reduced) {
  return reduced?.value
    ? { duration: 0 }
    : { duration: 0.32, ease: EASE }
}
