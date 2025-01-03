<template>
  <v-card class="elevation-12">
    <v-toolbar color="primary" dark flat>
      <v-toolbar-title>Login</v-toolbar-title>
    </v-toolbar>
    <v-card-text>
      <v-form @submit.prevent="handleSubmit">
        <v-text-field
          label="Username"
          v-model="username"
          prepend-icon="mdi-account"
          type="text"
          required
        />
        <v-text-field
          label="Password"
          v-model="password"
          prepend-icon="mdi-lock"
          type="password"
          required
        />
        <v-btn type="submit" color="primary" :loading="authStore.loading" class="mr-2">Login</v-btn>
        <NuxtLink to="/signup">
          <v-btn color="secondary">Signup</v-btn>
        </NuxtLink>
        <div v-if="authStore.error" class="error mt-2">{{ authStore.error }}</div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

export default {
  setup() {
    const username = ref('');
    const password = ref('');
    const authStore = useAuthStore();

    const handleSubmit = () => {
      authStore.login(username.value, password.value);
    };

    return {
      username,
      password,
      handleSubmit,
      authStore,
    };
  },
};
</script>

<style lang="scss" scoped>
.error {
  color: #f00;
  font-size: 14px;
}
</style>