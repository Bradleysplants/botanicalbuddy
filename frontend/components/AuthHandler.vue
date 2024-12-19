<template>
    <div>
      </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        authReady: false,
      };
    },
    mounted() {
      // Check for $auth in mounted() with a delay
      let authCheckInterval = setInterval(() => {
        if (this.$auth) {
          this.authReady = true;
          clearInterval(authCheckInterval);
          console.trace('this.$auth is ready (AuthHandler):', this.$auth);
          // Optionally emit an event to notify other components
          this.$emit('auth-ready'); 
        }
      }, 100); // Check every 100 milliseconds
    },
  };
  </script>