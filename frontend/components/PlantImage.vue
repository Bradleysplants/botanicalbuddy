<template>
    <div v-if="imageUrl">
      <img :src="imageUrl" alt="Plant" class="w-48 h-48 object-cover rounded-lg" />
    </div>
  </template>
  
  <script>
  export default {
    props: {
      imageUrl: {
        type: String,
        required: true,
      },
    },
  };
  </script>