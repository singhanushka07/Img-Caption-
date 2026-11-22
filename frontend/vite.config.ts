import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/caption': 'http://127.0.0.1:8000',
      '/vqa': 'http://127.0.0.1:8000',
      '/stats': 'http://127.0.0.1:8000',
      '/styles': 'http://127.0.0.1:8000',
      '/languages': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/usage': 'http://127.0.0.1:8000',
    },
  },
})
