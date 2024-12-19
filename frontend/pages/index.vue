<template>
  <v-app>
    <v-navigation-drawer v-model="drawer" location="left" temporary>
      <v-list>
        <v-list-item :to="{ name: 'index' }" prepend-icon="mdi-home">
          <v-list-item-title>Home</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="!authStore.isAuthenticated" :to="{ name: 'login' }" prepend-icon="mdi-login">
          <v-list-item-title>Login</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="authStore.isAuthenticated" :to="{ name: 'profile' }" prepend-icon="mdi-account">
          <v-list-item-title>Profile</v-list-item-title>
        </v-list-item>

        <v-list-item v-if="authStore.isAuthenticated" @click="logout" prepend-icon="mdi-logout">
          <v-list-item-title>Logout</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar>
      <v-app-bar-nav-icon @click="drawer =!drawer"></v-app-bar-nav-icon>
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
import { useAuthStore } from '../stores/auth';

export default {
  data() {
    return {
      drawer: false,
    };
  },
  setup() {
    const authStore = useAuthStore();

    if (authStore.isAuthenticated) {
      // Handle the case when the user is already authenticated
    }

    watch(
      () => authStore.isAuthenticated,
      (newValue) => {
        if (newValue) {
          // Handle the case when the user becomes authenticated
        } else {
          // Handle the case when the user becomes unauthenticated
        }
      }
    );

    return {
      authStore,
    };
  },
  methods: {
    async logout() {
      await this.authStore.logout();
      this.$router.push('/');
    },
  },
};
</script>