<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" sm="6" md="4" lg="3">
        <LoginWindow @login-submitted="handleLogin" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import LoginWindow from '@/components/LoginWindow.vue'; // Adjust the path
import { useAuthStore } from '@/stores/auth'; // Import your auth store
import { useRouter } from 'vue-router';

export default {
  components: {
    LoginWindow,
  },
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();

    const handleLogin = async ({ username, password }) => {
      try {
        await authStore.login(username, password);
        if (authStore.isAuthenticated) {
          router.push('/'); // Redirect on successful login
        }
      } catch (error) {
        // Error is handled and displayed within LoginWindow
        console.error("Login failed in login.vue", error);
      }
    };

    return {
      handleLogin,
    };
  },
};
</script>

<style scoped>
/* You can add specific styling for the login page here if needed */
</style>
