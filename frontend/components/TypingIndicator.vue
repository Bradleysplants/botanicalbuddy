<template>
    <div v-if="isTyping" class="typing-indicator">
      <span>.</span><span>.</span><span>.</span>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      isTyping: {
        type: Boolean,
        required: true,
      },
    },
  };
  </script>