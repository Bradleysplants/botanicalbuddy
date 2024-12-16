<!-- pages/plantdata.vue -->
<template>
    <div>
      <h1>Plant Data</h1>
      <ul>
        <li v-for="plant in plantData" :key="plant.id">
          <strong>Plant Name:</strong> {{ plant.plant_name }}<br>
          <strong>Scientific Name:</strong> {{ plant.scientific_name }}<br>
          <strong>Description:</strong> {{ plant.description }}<br>
          <strong>Care Instructions:</strong> {{ plant.care_instructions }}<br>
          <strong>Soil Type:</strong> {{ plant.soil_type }}<br>
          <strong>Water Requirements:</strong> {{ plant.water_requirements }}<br>
          <strong>Sunlight Requirements:</strong> {{ plant.sunlight_requirements }}<br>
          <strong>Created At:</strong> {{ plant.created_at }}
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        plantData: []
      };
    },
    async asyncData({ $axios }) {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          return { plantData: [] };
        }
  
        const response = await $axios.get('http://localhost:8000/api/plantdata/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
  
        return { plantData: response.data };
      } catch (error) {
        console.error('Fetch plant data failed:', error);
        return { plantData: [] };
      }
    }
  };
  </script>