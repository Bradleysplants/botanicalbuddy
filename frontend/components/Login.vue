<template>
  <div class="container mx-auto p-4">
    <h2 class="text-2xl font-bold mb-4">Login</h2>
    <form @submit.prevent="login">
      <div class="mb-4">
        <label for="username" class="block text-gray-700 font-medium mb-2">Username:</label>
        <input type="text" id="username" v-model="username" class="border border-gray-400 rounded px-3 py-2 w-full">
      </div>
      <div class="mb-4">
        <label for="password" class="block text-gray-700 font-medium mb-2">Password:</label>
        <input type="password" id="password" v-model="password" class="border border-gray-400 rounded px-3 py-2 w-full">
      </div>
      <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded">Login</button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'; // Import ref
import { useAuthStore } from '~/stores/auth'; // Import useAuthStore
import { useRouter } from 'nuxt/app'; // Import useRouter

export default {
  setup() {
    const username = ref('');
    const password = ref('');
    const authStore = useAuthStore();
    const router = useRouter();

    const login = async () => {
      try {
        await authStore.login(username.value, password.value);
        // Redirect after successful login
        router.push('/chat');
      } catch (error) {
        console.error('Login error:', error);
        // Handle login error (e.g., show error message)
      }
    };

    return { username, password, login };
  },
};
</script>