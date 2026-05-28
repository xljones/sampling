import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./frontend-src/vitest.setup.js'],
    include: ['frontend-src/**/*.test.{js,jsx}'],
  },
});
