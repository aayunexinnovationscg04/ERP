import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Driver ERP SPA. In production nginx serves it under /pilot/ on erp.aayunexinnovations.com;
// API calls are same-origin ("/api/..."). base must match the nginx location so built
// asset URLs resolve to /pilot/assets/... In dev, proxy /api to Django on :8000.
export default defineConfig({
  base: '/pilot/',
  plugins: [vue()],
  server: {
    port: 5174,
    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
