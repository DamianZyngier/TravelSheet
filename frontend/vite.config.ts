import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './', // Używamy relatywnych ścieżek, żeby działało na GitHub Pages
  build: {
    outDir: '../docs', // Budujemy do folderu docs w głównym katalogu
    emptyOutDir: true, // Czyścimy docs przed każdym buildem
  }
})
