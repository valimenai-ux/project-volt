import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The app lives at a repo subpath on GitHub Pages
// (https://valimenai-ux.github.io/project-volt/). A wrong base is the
// single most common cause of a blank deployed page.
export default defineConfig({
  base: '/project-volt/',
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsInlineLimit: 0,
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
})
