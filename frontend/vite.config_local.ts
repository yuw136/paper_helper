import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    target: 'esnext',
    outDir: 'build',
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      // Forward all requests starting with /api to Python backend
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '') // Backend doesn't have /api prefix
      },
    },
  },
});
