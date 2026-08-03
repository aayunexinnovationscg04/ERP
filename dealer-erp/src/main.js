import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import './style.css'
import 'leaflet/dist/leaflet.css'
// Self-hosted variable font (matches Pilot/Admin) — no external font CDN,
// so there's no third-party network request or FOUC risk in production.
import '@fontsource-variable/inter/wght.css'

// Fix Leaflet's default marker icon paths under a bundler.
import L from 'leaflet'
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'
L.Icon.Default.mergeOptions({ iconUrl, iconRetinaUrl, shadowUrl })

createApp(App).use(router).mount('#app')
