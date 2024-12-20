<template>
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

      <v-list-item v-if="authStore.isAuthenticated">
        <LogoutButton />
      </v-list-item>
    </v-list>
  </v-navigation-drawer>

  <v-app-bar>
    <v-app-bar-nav-icon @click="drawer =!drawer"></v-app-bar-nav-icon>
    <v-toolbar-title>Botanical Buddy</v-toolbar-title>
  </v-app-bar>
</template>

<script>
import { useAuthStore } from '../stores/auth.js'
import LogoutButton from './LogoutButton.vue';

export default {
  components: { LogoutButton },
  data() {
    return {
      drawer: false,
    };
  },
  setup() {
    const authStore = useAuthStore()

    return { authStore }
  },
};
</script>