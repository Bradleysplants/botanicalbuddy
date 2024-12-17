<template>
  <div class="container mx-auto p-4">
    <h2 class="text-2xl font-bold mb-4">Botanical Buddy</h2>
    <div v-if="chatStore.loading">Loading...</div>
    <div v-else class="chat-window border border-gray-400 rounded h-96 overflow-y-auto p-4 mb-4">
      <PlantImage :imageUrl="plantImageUrl" v-if="plantImageUrl" />
      <div v-for="(message, index) in chatStore.messages" :key="index" class="message mb-2" :class="{ 'user-message': message.isUser }">
        <pre v-if="typeof message.text === 'object'">{{ message.text }}</pre>
        <p v-else>{{ message.text }}</p>
        <UserFeedback v-if="!message.isUser && !isLastMessage(index)" /> 
      </div>
      <TypingIndicator :isTyping="isTyping" />
    </div>
    <ErrorMessage :message="errorMessage" />
    <SuggestedQuestions :questions="suggestedQuestions" />
    <form @submit.prevent="sendMessage">
      <input type="text" v-model="newMessage" placeholder="Type your message..." class="border border-gray-400 rounded px-3 py-2 w-full">
      <button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded mt-2">Send</button>
    </form>
  </div>
</template>

<script>
import { ref, computed } from 'vue';
import { useChatStore } from '~/stores/chat';
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