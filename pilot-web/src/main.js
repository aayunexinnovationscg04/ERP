import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import './style.css'
// Self-hosted variable font (matches Dealer/Admin) — replaces the Google
// Fonts CDN link in index.html so there's no third-party network request.
import '@fontsource-variable/plus-jakarta-sans/wght.css'


createApp(App).use(router).mount('#app')
