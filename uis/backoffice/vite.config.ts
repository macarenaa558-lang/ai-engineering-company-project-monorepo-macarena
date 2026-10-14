import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendTarget =
  process.env.VITE_BACKEND_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/auth': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/users': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/profiles': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/suppliers': {
        target: backendTarget,
        changeOrigin: true,
      },
      '/inventory': {
        target: backendTarget,
        changeOrigin: true,
      },
    },
  },
})