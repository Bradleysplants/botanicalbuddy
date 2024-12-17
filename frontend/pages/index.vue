<template>
    <div class="container mx-auto p-4 text-center">
      <h1 class="text-4xl font-bold mb-4">Welcome to Botanical Buddy!</h1>
      <p class="text-lg mb-6">Your AI-powered guide to the world of plants.</p>
  
      <div v-if="!$auth.loggedIn" class="mb-4">
        <NuxtLink to="/signup" class="bg-green-500 hover:bg-green-700 text-white font-medium py-2 px-4 rounded mr-2">Sign Up</NuxtLink>
        <NuxtLink to="/login" class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded">Login</NuxtLink>
      </div>
  
      <div v-else>
        <NuxtLink to="/chat" class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded">Go to Chat</NuxtLink>
      </div>
  
      <div class="features mt-12">
        <h2 class="text-2xl font-bold mb-4">Features</h2>
        <ul class="list-disc list-inside text-left">
          <li>Ask any plant-related question and get instant answers.</li>
          <li>Learn about different plant species, their care, and their uses.</li>
          <li>Diagnose plant diseases and get treatment recommendations.</li>
          <li>Discover fun facts and interesting information about plants.</li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    // You can add any necessary data or methods here
  };
  </script>