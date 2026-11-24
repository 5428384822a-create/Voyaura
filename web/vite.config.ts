import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: process.env.VOYAURA_DEV_API_URL ?? 'http://127.0.0.1:8018',
        changeOrigin: true,
      },
    },
  },
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Voyaura',
        short_name: 'Voyaura',
        description: 'Plan the journey. Shape the story.',
        theme_color: '#ed683e',
        background_color: '#faf9f6',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: '/voyaura-mark.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any maskable',
          },
        ],
      },
    }),
  ],
})
