<template>
    <div class="container mx-auto p-4">
      <h2 class="text-2xl font-bold mb-4">Sign Up</h2>
      <form @submit.prevent="signup">
        <div class="mb-4">
          <label for="username" class="block text-gray-700 font-medium mb-2">Username:</label>
          <input type="text" id="username" v-model="username" class="border border-gray-400 rounded px-3 py-2 w-full" required>
        </div>
        <div class="mb-4">
          <label for="email" class="block text-gray-700 font-medium mb-2">Email:</label>
          <input type="email" id="email" v-model="email" class="border border-gray-400 rounded px-3 py-2 w-full" required>
        </div>
        <div class="mb-4">
          <label for="password" class="block text-gray-700 font-medium mb-2">Password:</label>
          <input type="password" id="password" v-model="password" class="border border-gray-400 rounded px-3 py-2 w-full" required>
        </div>
        <button type="submit" class="bg-green-500 hover:bg-green-700 text-white font-medium py-2 px-4 rounded">Sign Up</button>
      </form>
      <ErrorMessage :message="errorMessage" />
    </div>
  </template>
  
  <script>
  import { ref } from 'vue';
  import { useAuthStore } from '~/stores/auth';
  import { useRouter } from 'nuxt/app';
  import ErrorMessage from '~/components/ErrorMessage.vue';
  
  export default {
    components: {
      ErrorMessage,
    },
    setup() {
      const username = ref('');
      const email = ref('');
      const password = ref('');
      const authStore = useAuthStore();
      const router = useRouter();
      const errorMessage = ref('');
  
      const signup = async () => {
        try {
          await authStore.signup(username.value, email.value, password.value); 
          router.push('/login'); 
        } catch (error) {
          console.error('Signup error:', error);
          errorMessage.value = 'Signup failed. Please try again.'; 
        }
      };
  
      return { username, email, password, signup, errorMessage };
    },
  };
  </script>