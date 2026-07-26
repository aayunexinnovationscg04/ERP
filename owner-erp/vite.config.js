import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Owner ERP SPA. In production it is served by nginx at the root of :8090, so API
// calls are same-origin ("/api/..."). In dev, proxy /api to Django on :8000.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  build: { outDir: 'dist', emptyOutDir: true },
})
