import { defineStore } from 'pinia';

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    plantName: null, 
    loading: false,
  }),
  actions: {
    async initializeChat(plantName) { 
      this.plantName = plantName;
      this.messages = []; 
      this.loading = true;
      try {
        const response = await fetch(`/api/get_plant_data/?name=${plantName}`);
        const data = await response.json();
        this.messages.push({ text: `Here's some information about ${plantName}:`, isUser: false });
        this.messages.push({ text: JSON.stringify(data, null, 2), isUser: false }); 
      } catch (error) {
        console.error('Error fetching plant data:', error);
        this.messages.push({ text: 'Error fetching plant data.', isUser: false });
      } finally {
        this.loading = false;
      }
    },
    async sendMessage(message) {
      if (message.trim() === '') return;

      this.messages.push({ text: message, isUser: true });

      try {
        const response = await fetch('/api/ask_botanical_question/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: message, plant_name: this.plantName }),
        });
        const data = await response.json();
        this.messages.push({ text: data.answer, isUser: false });
      } catch (error) {
        console.error('Error sending message:', error);
        this.messages.push({ text: 'Error sending message.', isUser: false });
      }
    },
  },
});