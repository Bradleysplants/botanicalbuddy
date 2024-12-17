<template>
    <div>
      <header class="bg-gray-800 text-white p-4">
        <div class="container mx-auto flex justify-between items-center">
          <NuxtLink to="/" class="text-xl font-bold">Botanical Buddy</NuxtLink>
          <nav>
            <ul class="flex space-x-4">
              <li v-if="$auth.loggedIn"><NuxtLink to="/chat">Chat</NuxtLink></li>
              <li v-if="!$auth.loggedIn"><NuxtLink to="/login">Login</NuxtLink></li>
              <li v-if="!$auth.loggedIn"><NuxtLink to="/signup">Signup</NuxtLink></li>
              <li v-if="$auth.loggedIn"><Logout /></li> 
            </ul>
          </nav>
        </div>
      </header>
      <main class="container mx-auto p-4">
        <Nuxt />
      </main>
      <footer class="bg-gray-200 text-gray-600 p-4 mt-8">
        <div class="container mx-auto text-center">
          &copy; 2023 Botanical Buddy
        </div>
      </footer>
    </div>
  </template>
  
  <script>
  import Logout from '~/components/Logout.vue'; // Assuming you have the Logout component
  
  export default {
    components: {
      Logout,
    },
  };
  </script>