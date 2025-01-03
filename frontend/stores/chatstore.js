// stores/chatstore.js
import { defineStore } from 'pinia';
import DOMPurify from 'dompurify';
import apiService from '../servivces/apiService'; // Import the API service

const sanitize = DOMPurify.sanitize;

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    loading: false,
    botIsTyping: false,
  }),
  actions: {
    async sendMessage(message) {
      if (message.trim() === '') return;

      const sanitizedMessage = sanitize(message);
      this.messages.push({ text: sanitizedMessage, isUser: true });
      this.botIsTyping = true;

      try {
        const response = await apiService.askBotanicalQuestion(sanitizedMessage);
        this.messages.push({ text: response.answer, isUser: false });
      } catch (error) {
        console.error('Error sending message:', error);
        this.messages.push({ text: 'Error sending message. Please try again.', isUser: false });
      } finally {
        this.botIsTyping = false;
      }
    },
    clearChat() {
      this.messages = [];
    },
  },
});