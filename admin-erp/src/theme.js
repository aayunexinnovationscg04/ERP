import { ref } from 'vue'

const STORAGE_KEY = 'fgx_theme'

function getInitialTheme() {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored === 'light' ? 'light' : 'dark'
}

const theme = ref(getInitialTheme())
document.documentElement.setAttribute('data-theme', theme.value)

function applyTheme(next) {
  theme.value = next
  document.documentElement.setAttribute('data-theme', next)
  localStorage.setItem(STORAGE_KEY, next)
}

export function useTheme() {
  function toggleTheme() {
    applyTheme(theme.value === 'dark' ? 'light' : 'dark')
  }
  return { theme, toggleTheme }
}
