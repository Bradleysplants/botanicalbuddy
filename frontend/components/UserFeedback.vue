<template>
    <div>
      <button @click="sendFeedback('positive')" class="mr-2">👍</button>
      <button @click="sendFeedback('negative')">👎</button>
    </div>
  </template>
  
  <script>
  export default {
    methods: {
      sendFeedback(type) {
        // Send feedback to the backend or store it in Pinia
        console.log(`Feedback sent: ${type}`);
      },
    },
  };
  </script>