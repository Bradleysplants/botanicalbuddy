<template>
    <a href="#" @click.prevent="logout" class="text-blue-500 hover:underline">Logout</a>
  </template>
  
  <script>
  export default {
    methods: {
      async logout() {
        try {
          const response = await fetch('/api/logout/', { method: 'POST' });
          // Handle successful logout (e.g., clear token, redirect to login)
        } catch (error) {
          console.error('Logout error:', error);
          // Handle logout error
        }
      },
    },
  };
  </script>