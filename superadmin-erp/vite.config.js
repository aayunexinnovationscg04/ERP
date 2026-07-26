import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Super Admin ERP SPA. Served by nginx under the /admin/ path on the single
// erp.aayunexinnovations.com host (Owner ERP lives at /dealer/). API is same-origin ("/api/...").
// base must match the nginx location so built asset URLs resolve to /admin/assets/...
// In dev, proxy /api to Django on :8000.
export default defineConfig({
  base: '/admin/',
  plugins: [vue()],
  server: {
    port: 5175,
    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
