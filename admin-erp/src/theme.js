import { ref } from 'vue'

const STORAGE_KEY = 'fgx_theme'

// The user's explicit choice wins; otherwise follow the device setting.
function getInitialTheme() {
  let stored = null
  try { stored = localStorage.getItem(STORAGE_KEY) } catch (e) { /* storage blocked */ }
  if (stored === 'light' || stored === 'dark') return stored
  return matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const theme = ref(getInitialTheme())
document.documentElement.setAttribute('data-theme', theme.value)

let transitionTimer = null
function applyTheme(next) {
  const root = document.documentElement
  // Briefly transition every surface's color/background/border instead of a
  // hard instant snap, then drop the class so it doesn't linger and affect
  // unrelated hover/interaction transitions. Skipped entirely under
  // prefers-reduced-motion via the matching CSS media query, not here.
  root.classList.add('theme-transition')
  clearTimeout(transitionTimer)
  transitionTimer = setTimeout(() => root.classList.remove('theme-transition'), 340)

  theme.value = next
  root.setAttribute('data-theme', next)
  try { localStorage.setItem(STORAGE_KEY, next) } catch (e) { /* storage blocked */ }
}

export function useTheme() {
  function toggleTheme() {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark')
  }
  return { theme, toggleTheme }
}
