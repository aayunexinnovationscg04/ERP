import { ref } from 'vue'

const STORAGE_KEY = 'fgx_theme'

function getInitialTheme() {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored === 'light' ? 'light' : 'dark'
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
  localStorage.setItem(STORAGE_KEY, next)
}

export function useTheme() {
  function toggleTheme() {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark')
  }
  return { theme, toggleTheme }
}
