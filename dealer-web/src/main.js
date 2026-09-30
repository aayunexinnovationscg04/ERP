import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import './style.css'
// Self-hosted variable font (matches Pilot/Admin) — no external font CDN,
// so there's no third-party network request or FOUC risk in production.
import '@fontsource-variable/plus-jakarta-sans/wght.css'


createApp(App).use(router).mount('#app')
