<!-- pages/compute.vue -->
<template>
    <div>
      <h1>Compute</h1>
      <form @submit.prevent="compute">
        <div>
          <label for="vector_data">Vector Data:</label>
          <input type="text" id="vector_data" v-model="vectorData" required />
        </div>
        <div>
          <label for="temperature">Temperature:</label>
          <input type="number" id="temperature" v-model="temperature" required />
        </div>
        <div>
          <label for="top_k">Top K:</label>
          <input type="number" id="top_k" v-model="topK" required />
        </div>
        <div>
          <label for="system_message">System Message:</label>
          <input type="text" id="system_message" v-model="systemMessage" required />
        </div>
        <button type="submit">Compute</button>
      </form>
      <div v-if="result">
        <h2>Result:</h2>
        <pre>{{ result }}</pre>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        vectorData: '',
        temperature: 0.7,
        topK: 50,
        systemMessage: 'You are a helpful botanist.',
        result: null
      };
    },
    methods: {
      async compute() {
        try {
          const token = localStorage.getItem('token');
          if (!token) {
            this.$router.push('/login');
            return;
          }
  
          const response = await axios.post('http://localhost:8000/api/compute/', {
            vector_data: JSON.parse(this.vectorData),
            temperature: this.temperature,
            top_k: this.topK,
            system_message: this.systemMessage
          }, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
  
          this.result = response.data.result;
        } catch (error) {
          console.error('Compute failed:', error);
        }
      }
    }
  };
  </script>