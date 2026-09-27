// The admin console uses the light theme only (no dark mode, no switcher).
// Tokens for both themes still live in shared/design/tokens.css for the other portals.
document.documentElement.setAttribute('data-theme', 'light')
try { localStorage.removeItem('fgx_theme') } catch (e) { /* storage blocked */ }
