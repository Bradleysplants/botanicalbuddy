<!-- pages/retrieve.vue -->
<template>
    <div>
      <h1>Retrieve</h1>
      <form @submit.prevent="retrieve">
        <div>
          <label for="name">Name:</label>
          <input type="text" id="name" v-model="name" required />
        </div>
        <button type="submit">Retrieve</button>
      </form>
      <div v-if="results">
        <h2>Results:</h2>
        <ul>
          <li v-for="result in results" :key="result.id">
            <strong>Name:</strong> {{ result.name }}<br>
            <strong>Description:</strong> {{ result.description }}<br>
            <strong>Vector Data:</strong> {{ result.vector_data }}<br>
            <strong>Created At:</strong> {{ result.created_at }}
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        name: '',
        results: null
      };
    },
    methods: {
      async retrieve() {
        try {
          const token = localStorage.getItem('token');
          if (!token) {
            this.$router.push('/login');
            return;
          }
  
          const response = await axios.get(`http://localhost:8000/api/retrieve/?name=${this.name}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
  
          this.results = response.data.vector_data;
        } catch (error) {
          console.error('Retrieve failed:', error);
        }
      }
    }
  };
  </script>