<template>
  <div class="container mx-auto p-4">
    <h2 class="text-2xl font-bold mb-4">Login</h2> 
    <form @submit.prevent="login" class="space-y-4"> 
      <div>
        <label for="username" class="block text-gray-700 font-medium mb-2">Username:</label>
        <input 
          type="text" 
          id="username" 
          v-model="username" 
          class="border border-gray-400 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500" 
          aria-label="Username" 
          aria-required="true" 
          :aria-invalid="invalidUsername" 
        >
        <div v-if="invalidUsername" class="text-red-500 text-sm mt-1" role="alert"> 
          Please enter a valid username.
        </div>
      </div>
      <div>
        <label for="password" class="block text-gray-700 font-medium mb-2">Password:</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          class="border border-gray-400 rounded px-3 py-2 w-full focus:outline-none focus:ring-2 focus:ring-blue-500" 
          aria-label="Password" 
          aria-required="true" 
          :aria-invalid="invalidPassword" 
        >
        <div v-if="invalidPassword" class="text-red-500 text-sm mt-1" role="alert"> 
          Please enter a valid password.
        </div>
      </div>
      <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded">Login</button>
    </form>

    <div class="mt-4">
      <p class="text-gray-700">Don't have an account? <a href="#" @click.prevent="goToSignup" class="text-blue-500 hover:text-blue-700">Sign up</a></p>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useChatStore } from '~/stores/chatstore';
import PlantImage from '~/components/PlantImage.vue';
import UserFeedback from '~/components/UserFeedback.vue';
import TypingIndicator from '~/components/TypingIndicator.vue';
import ErrorMessage from '~/components/ErrorMessage.vue';
import SuggestedQuestions from '~/components/SuggestedQuestions.vue';

export default {
  components: {
    PlantImage,
    UserFeedback,
    TypingIndicator,
    ErrorMessage,
    SuggestedQuestions,
  },

  setup() {
    const chatStore = useChatStore();
    const newMessage = ref('');
    const isTyping = ref(false);
    const errorMessage = ref('');
    const suggestedQuestions = ref([]);
    const plantImageUrl = computed(() => {
      const plantData = chatStore.messages.find(msg => typeof msg.text === 'object');
      return plantData ? plantData.text.image_url : null; 
    });

    const sendMessage = async () => {
      if (newMessage.value.trim() === '') return;
      errorMessage.value = '';
      chatStore.sendMessage(newMessage.value);
      newMessage.value = '';
      isTyping.value = true; 
      // Simulate some delay for the typing indicator
      setTimeout(() => {
        isTyping.value = false;
      }, 1000);
    };

    const isLastMessage = (index) => index === chatStore.messages.length - 1;

    return {
      chatStore,
      newMessage,
      sendMessage,
      isTyping,
      errorMessage,
      suggestedQuestions,
      plantImageUrl,
      isLastMessage,
    };
  },
  async mounted() {
    try {
      await this.chatStore.initializeChat('Rose'); // Replace 'Rose' with the desired plant name
    } catch (error) {
      this.errorMessage = 'Failed to initialize chat.';
    }
  },
};
</script>