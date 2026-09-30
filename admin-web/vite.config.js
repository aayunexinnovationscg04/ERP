import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

// Admin ERP SPA, served from the root of admin.aayunexinnovations.com (own
// subdomain), so base is '/'. API calls are same-origin ("/api/..."). In dev,
// /api is proxied to Django (API_TARGET, default :8000).
export default defineConfig({
  base: '/',
  plugins: [vue()],
  resolve: {
    // Design system + shared components used by all three portals.
    alias: { '@shared': fileURLToPath(new URL('../shared', import.meta.url)) },
    // Files under ../shared have no node_modules of their own: resolve these
    // from this app so there is exactly one copy of each.
    dedupe: ['vue', 'vue-router', 'lucide-vue-next'],
  },
  server: {
    fs: { allow: ['..'] },
    port: 5175,
    proxy: { '/api': { target: process.env.API_TARGET || 'http://127.0.0.1:8000', changeOrigin: true } },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
