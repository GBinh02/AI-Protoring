import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    proxy: {
      // Ảnh snapshot giờ được phục vụ qua /api/snapshots/{filename} (có xác thực token),
      // nên chỉ cần proxy '/api' là đủ — không còn mount /snapshots tĩnh công khai ở backend nữa.
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
