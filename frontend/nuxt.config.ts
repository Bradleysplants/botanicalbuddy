import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  // ... other config

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


  build: {
      transpile: ['@sidebase/nuxt-auth']
  },

  compatibilityDate: '2024-12-16'
})