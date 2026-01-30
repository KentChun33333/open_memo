import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://v3.esbuild.run/renderer.html#configurationalterations
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
  },
  // Tailwind CSS will be processed via postcss, no special Vite config needed.
});