<!-- pages/store.vue -->
<template>
  <div>
    <h1>Store</h1>
    <form @submit.prevent="store">
      <div>
        <label for="vector_data">Vector Data:</label>
        <input type="text" id="vector_data" v-model="vectorData" required />
      </div>
      <div>
        <label for="name">Name:</label>
        <input type="text" id="name" v-model="name" required />
      </div>
      <div>
        <label for="description">Description:</label>
        <input type="text" id="description" v-model="description" required />
      </div>
      <button type="submit">Store</button>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      vectorData: '',
      name: '',
      description: ''
    };
  },
  methods: {
    async store() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          this.$router.push('/login');
          return;
        }

        const response = await axios.post('http://localhost:8000/api/store/', {
          vector_data: JSON.parse(this.vectorData),
          name: this.name,
          description: this.description
        }, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        alert('Data stored successfully');
      } catch (error) {
        console.error('Store failed:', error);
      }
    }
  }
};
</script>