<template>
  <v-app>
    <NavBar />

    <v-main v-if="!isLoading">
      <v-container fluid>
        <NuxtPage />
      </v-container>
    </v-main>

    <div v-if="isLoading" class="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div class="loader"></div>
    </div>
  </v-app>
</template>

<script>
import NavBar from '@/components/NavBar.vue';

export default {
  components: {
    NavBar,
  },
  data() {
    return {
      isLoading: true,
    };
  },
  mounted() {
    // Simulate a loading delay (replace with actual loading logic if needed)
    setTimeout(() => {
      this.isLoading = false; // Remove .value 
    }, 1000);
  },
};
</script>

<style>
/* Add loading spinner styles here */
.loader {
  border: 4px solid #f3f3f3;
  border-radius: 50%;
  border-top: 4px solid #3498db;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}
</style>