<template>
  <v-app>
    <AuthHandler @auth-ready="handleAuthReady" /> 

    <v-navigation-drawer v-model="drawer" location="left" temporary>
      <v-list>
        <v-list-item :to="{ name: 'index' }" prepend-icon="mdi-home">
          <v-list-item-title>Home</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="authReady && !$auth.loggedIn" :to="{ name: 'login' }" prepend-icon="mdi-login">
          <v-list-item-title>Login</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="authReady && $auth.loggedIn" :to="{ name: 'profile' }" prepend-icon="mdi-account">
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="authReady && $auth.loggedIn" @click="logout" prepend-icon="mdi-logout">
          <v-list-item-title>Logout</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Botanical Buddy</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <NuxtPage />
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
export default {
  components: {
    AuthHandler: () => import('@/components/AuthHandler.vue') // Import AuthHandler
  },
  data() {
    return {
      drawer: false,
      authReady: false, // Add authReady to data
    };
  },
  methods: {
    async logout() {
      await this.$auth.logout();
      this.$router.push('/');
    },
    handleAuthReady() {
  this.$nextTick(() => { // Update authReady in the next tick
    this.authReady = true;
  });
},

handleAuthReady() {
  this.$nextTick(() => { // Update authReady in the next tick
    this.authReady = true;
  });
}
  }
};
</script>