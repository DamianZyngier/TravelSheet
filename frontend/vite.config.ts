import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Keep relative for GitHub Pages, but dev server usually handles this
  build: {
    outDir: '../docs', // Budujemy do folderu docs w głównym katalogu
    emptyOutDir: true, // Czyścimy docs przed każdym buildem
  }
})
