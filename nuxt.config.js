export default {
  // Target: https://go.nuxtjs.dev/config-target
  target: 'static',

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    title: 'iem-webapp',
    htmlAttrs: {
      lang: 'en',
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  // Main is the entrypoint for all SCSS in our app.
  css: ['@/assets/scss/main.scss'],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: ['~/plugins/leaflet.client.js', '~/plugins/vuex-router-sync'],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/buefy
    // We're doing a custom build, so don't include
    // the pre-generated CSS.
    ['nuxt-buefy', { css: false }],
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    // https://go.nuxtjs.dev/content
    '@nuxt/content',
    // https://www.npmjs.com/package/nuxt-leaflet
    'nuxt-leaflet',
    '@nuxt/http',
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {},

  // Content module configuration: https://go.nuxtjs.dev/config-content
  content: {},

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {},

  // Env vars
  env: {
    geoserverUrl:
      process.env.GEOSERVER_URL || 'https://gs.mapventure.org/geoserver/wms',
    rasdamanUrl:
      process.env.GEOSERVER_URL || 'https://apollo.snap.uaf.edu/rasdaman/ows',
  },

  // Router customizations
  router: {
    extendRoutes(routes, resolve) {
      routes.push({
        path: '/report/community/:communityId',
        component: resolve(__dirname, 'pages/index'),
      })
      routes.push({
        path: '/report/:lat/:lng',
        component: resolve(__dirname, 'pages/index'),
      })
    },
  },
}
