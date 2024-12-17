<template>
    <div v-if="questions.length > 0">
      <p>Suggested questions:</p>
      <ul>
        <li v-for="question in questions" :key="question">{{ question }}</li>
      </ul>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      questions: {
        type: Array,
        required: true,
      },
    },
  };
  </script>