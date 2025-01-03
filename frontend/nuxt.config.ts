import { defineNuxtConfig } from 'nuxt/config'

export default defineNuxtConfig({
  // Router: https://go.nuxtjs.dev/config-router
  router: {
    },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    '~/assets/main.css', 'vuetify/styles',
  ],

  // Plugins: https://go.nuxtjs.dev/config-plugins
  plugins: [
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: ['@nuxtjs/tailwindcss', '@pinia/nuxt', ['@sidebase/nuxt-auth', {
    auth: [
      {
        isEnabled: true,
        disableServerSideAuth: false,
        originEnvKey: 'AUTH_ORIGIN',
        baseURL: 'http://localhost:3000/api',
        provider: {
          id: 'auth0',
          type: 'oauth',
          clientId: process.env.AUTH0_CLIENT_ID,
          clientSecret: process.env.AUTH0_CLIENT_SECRET,
          domain: process.env.AUTH0_DOMAIN,
          authorizationURL: 'https://your-auth0-domain.com/authorize',
          tokenURL: 'https://your-auth0-domain.com/oauth/token',
          userInfoURL: 'https://your-auth0-domain.com/userinfo',
        },
        sessionRefresh: {
          enablePeriodically: true,
          enableOnWindowFocus: true,
        },
      },
    ],
  }], 'vuetify-nuxt-module',
],
    
  // Proxy: https://go.nuxtjs.dev/config-proxy
  nitro: {
    routeRules: {
      '/api/**': { 
        proxy: 'http://localhost:8000/api/**' 
      },
      '/session': { 
        proxy: 'http://localhost:8000/session' 
      },
      '/login': { // Add this proxy rule
        proxy: 'http://localhost:8000/login/'
      },
      '/login/**': { // Optionally, proxy subpaths under /login if needed
        proxy: 'http://localhost:8000/login/**'
      }
    }
  },


  vuetify: {
    moduleOptions: {
      
    },
        vuetifyOptions: {
          icons: {
              defaultSet: 'mdi',
            sets: ['mdi', 'fa']
      },
    },
  },

  // Runtime Config: https://go.nuxtjs.dev/config-runtime-config
  runtimeConfig: {
    yourOrigin: '/frontend',
    auth: {
      // You can add any auth-related runtime config here
    },
    env: {
      API_BASE_URL: process.env.NUXT_ENV_API_BASE_URL || '/api', // Use environment variable for base URL
    },
  },

  // Vite: https://go.nuxtjs.dev/config-vite
  vite: {
    ssr: {
      noExternal: ['vuetify'], 
    },
    define: {
    },
  },

  // Build: https://go.nuxtjs.dev/config-build
  build: {
    transpile: ['@sidebase/nuxt-auth', 'vuetify'],
  },

  // Compatibility: https://go.nuxtjs.dev/config-compatibility
  compatibilityDate: '2024-12-16',
})