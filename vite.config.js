import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  root: 'frontend-src',
  build: { outDir: '../dist', emptyOutDir: true },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': process.env.API_URL || 'http://localhost:5001',
    },
  },
});
