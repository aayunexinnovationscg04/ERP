import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Super Admin ERP SPA. Served by nginx on :8091; API is same-origin ("/api/...").
// In dev, proxy /api to Django on :8000.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5175,
    proxy: { '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true } },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
