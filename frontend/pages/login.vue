<!-- pages/login.vue -->
<template>
    <div>
      <h1>Login</h1>
      <form @submit.prevent="login">
        <div>
          <label for="username">Username:</label>
          <input type="text" id="username" v-model="username" required />
        </div>
        <div>
          <label for="password">Password:</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <button type="submit">Login</button>
      </form>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        username: '',
        password: ''
      };
    },
    methods: {
      async login() {
        try {
          const response = await axios.post('http://localhost:8000/api/auth/', {
            username: this.username,
            password: this.password
          });
          const token = response.data.token;
          localStorage.setItem('token', token);
          this.$router.push('/chat');
        } catch (error) {
          console.error('Login failed:', error);
        }
      }
    }
  };
  </script>