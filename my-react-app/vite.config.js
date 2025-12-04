import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/streamlit': {
        target: 'http://localhost:8501',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/streamlit/, ''),
        ws: true,
      },
      '/_stcore': {
        target: 'http://localhost:8501',
        changeOrigin: true,
        ws: true,
      },
      '/static': {
        target: 'http://localhost:8501',
        changeOrigin: true,
      },
      '/vendor': {
        target: 'http://localhost:8501',
        changeOrigin: true,
      },
      '/component': {
        target: 'http://localhost:8501',
        changeOrigin: true,
      },
    },
  },
})
