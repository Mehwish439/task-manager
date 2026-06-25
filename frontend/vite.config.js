import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  base: './', // Important for relative paths (e.g., cPanel deployment)
  server: {
    port: 5173
  },
  resolve: {
    alias: {
      // Explicitly map @ to src folder
      '@': path.resolve(__dirname, 'src')
    },
    extensions: ['.js', '.vue', '.json'] // Make sure Vite resolves these file types automatically
  }
})
