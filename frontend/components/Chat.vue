<template>
    <div class="container mx-auto p-4">
      <h2 class="text-2xl font-bold mb-4">Botanical Buddy</h2>
      <div class="chat-window border border-gray-400 rounded h-96 overflow-y-auto p-4 mb-4">
        <div v-for="(message, index) in messages" :key="index" class="message mb-2" :class="{ 'user-message': message.isUser }">
          {{ message.text }}
        </div>
      </div>
      <form @submit.prevent="sendMessage">
        <input type="text" v-model="newMessage" placeholder="Type your message..." class="border border-gray-400 rounded px-3 py-2 w-full">
        <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded mt-2">Send</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        newMessage: '',
        messages: [],
        plantName: 'Rose', // Replace with the actual plant name you want to search for
        loading: false,
      };
    },
    async mounted() {
      this.loading = true;
      try {
        const response = await fetch(`/api/get_plant_data/?name=${this.plantName}`);
        const data = await response.json();
        this.messages.push({ text: `Here's some information about ${this.plantName}:`, isUser: false });
        this.messages.push({ text: JSON.stringify(data), isUser: false }); // Assuming the response is JSON
      } catch (error) {
        console.error('Error fetching plant data:', error);
        this.messages.push({ text: 'Error fetching plant data.', isUser: false });
      } finally {
        this.loading = false;
      }
    },
    methods: {
      async sendMessage() {
        if (this.newMessage.trim() === '') return;
  
        this.messages.push({ text: this.newMessage, isUser: true });
        this.newMessage = ''; // Clear input field
  
        try {
          const response = await fetch('/api/ask_botanical_question/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: this.newMessage, plant_name: this.plantName }),
          });
          const data = await response.json();
          this.messages.push({ text: data.answer, isUser: false });
        } catch (error) {
          console.error('Error sending message:', error);
          this.messages.push({ text: 'Error sending message.', isUser: false });
        }
      },
    },
  };
  </script>