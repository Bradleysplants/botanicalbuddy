// services/apiService.js
import axios from 'axios';

const API_BASE_URL = process.env.NUXT_ENV_API_BASE_URL || '/api'; // Use environment variable for base URL

// Add an interceptor to include the token in the Authorization header
axios.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Token ${authStore.token}`; // Or 'Bearer' depending on your backend
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

const apiService = {
  async getPlantData(plantName) {
    try {
      const response = await axios.get(`${API_BASE_URL}/get_plant_data/`, {
        params: { name: plantName },
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching plant data:', error);
      throw error; // Re-throw to be handled by the component or store
    }
  },

  async askBotanicalQuestion(query, plantName) {
    try {
      const response = await axios.post(`${API_BASE_URL}/ask/`, {
        query: query,
        plant_name: plantName,
      });
      return response.data;
    } catch (error) {
      console.error('Error asking botanical question:', error);
      throw error;
    }
  },

  async login(username, password) {
    try {
      const response = await axios.post(`${API_BASE_URL}/login/`, {
        username: username,
        password: password,
      });
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  async signup(username, email, password) {
    try {
      const response = await axios.post(`${API_BASE_URL}/signup/`, {
        username: username,
        email: email,
        password: password,
      });
      return response.data;
    } catch (error) {
      console.error('Signup error:', error);
      throw error;
    }
  },

  async logout() {
    try {
      const response = await axios.post(`${API_BASE_URL}/logout/`);
      return response.data;
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  },

  async uploadImage(imageData, plantId) {
    try {
      const formData = new FormData();
      formData.append('image', imageData);
      formData.append('plant_id', plantId);

      const response = await axios.post(`${API_BASE_URL}/upload_image/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading image:', error);
      throw error;
    }
  },

  async getChatHistory() {
    try {
      const response = await axios.get(`${API_BASE_URL}/historical_chat_list/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching chat history:', error);
      throw error;
    }
  },

  async getChatDetail(chatId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/chat_detail/${chatId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching chat detail:', error);
      throw error;
    }
  },

  async createNewChat(plantName) {
    try {
      const response = await axios.post(`${API_BASE_URL}/chat/`, { plant_name: plantName });
      return response.data;
    } catch (error) {
      console.error('Error creating new chat:', error);
      throw error;
    }
  },

  async sendMessageToChat(chatId, text) {
    try {
      const response = await axios.post(`${API_BASE_URL}/messages/`, { chat_id: chatId, text: text });
      return response.data;
    } catch (error) {
      console.error('Error sending message to chat:', error);
      throw error;
    }
  },
};

export default apiService;