import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  // ... other config

  // Add the proxy configuration here
  nitro: {
    routeRules: {
      '/api/**': { 
        proxy: 'http://localhost:8000/api/**' // Proxy all requests under /api to your Django backend
      },
      '/session': { 
        proxy: 'http://localhost:8000/session' // Proxy /session to your Django backend
      },
        'api/session': { proxy: 'http://localhost:8000/session' }, 

    }
  },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    ['@sidebase/nuxt-auth', {
      providers: [
        {
          id: 'auth0',
          type: 'oauth2',
          clientId: process.env.AUTH0_CLIENT_ID,
          clientSecret: process.env.AUTH0_CLIENT_SECRET,
          issuer: process.env.AUTH0_ISSUER,
          authorizationURL: `${process.env.AUTH0_ISSUER}/authorize`,
          tokenURL: `${process.env.AUTH0_ISSUER}/oauth/token`,
        }
      ],
      enableGlobalAppMiddleware: true,
      basePath: '/auth',
    }],
  ],

  auth: {
    originEnvKey: 'NUXT_YOUR_ORIGIN'
  },
  runtimeConfig: {
    yourOrigin: ''
  },

  vite: {
    ssr: {
      noExternal: ['vuetify'], 
    },
  },


  build: {
    transpile: ['@sidebase/nuxt-auth']
  },

  compatibilityDate: '2024-12-16'
})