<!-- pages/chat.vue -->
<template>
    <div>
      <h1>Chat with the Botanist</h1>
      <div class="chat-container">
        <div class="chat-box">
          <div v-for="(message, index) in messages" :key="index" :class="['message', message.sender]">
            <strong>{{ message.sender }}:</strong> {{ message.text }}
          </div>
        </div>
        <div class="input-container">
          <input type="text" v-model="userInput" placeholder="Type your message..." @keyup.enter="sendMessage" />
          <button @click="sendMessage">Send</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        userInput: '',
        messages: [],
        temperature: 0.7,
        topK: 50,
        systemMessage: 'You are a knowledgeable botanist.'
      };
    },
    methods: {
      async sendMessage() {
        if (this.userInput.trim() === '') return;
  
        // Add user message to the chat
        this.messages.push({ sender: 'User', text: this.userInput });
  
        try {
          const token = localStorage.getItem('token');
          if (!token) {
            this.$router.push('/login');
            return;
          }
  
          // Send the message to the backend
          const response = await axios.post('http://localhost:8000/api/compute/', {
            vector_data: this.userInput.split(' ').map(Number), // Convert input to vector data
            temperature: this.temperature,
            top_k: this.topK,
            system_message: this.systemMessage
          }, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
  
          // Add agent response to the chat
          this.messages.push({ sender: 'Botanist', text: response.data