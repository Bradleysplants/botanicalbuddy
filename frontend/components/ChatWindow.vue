<template>
  <v-card>
    <v-card-title class="text-h6 pa-4">
      Botanical Buddy
    </v-card-title>
    <v-card-text style="height: 400px;" class="overflow-y-auto px-4 pb-2" ref="messageList" aria-live="polite" aria-relevant="additions" role="log">
      <div v-if="chatStore.messages.length === 0" class="text-center py-6">
        Ask me anything about your plants! Just type your question below.
      </div>
      <div v-else>
        <div
          v-for="(message, index) in chatStore.messages"
          :key="message.text + index"
          class="mb-2"
        >
          <div v-if="message.isUser" class="d-flex align-start justify-end">
            <v-chip color="primary" text-color="white" class="ml-2">{{ message.text }}</v-chip>
            <div class="font-weight-bold">You</div>
          </div>
          <div v-else class="d-flex align-start justify-start">
            <div class="font-weight-bold">Botanical Buddy</div>
            <v-chip color="grey-lighten-3" class="ml-2">
              {{ message.text }}
            </v-chip>
          </div>
        </div>
        <div v-if="chatStore.botIsTyping" class="d-flex align-start justify-start mb-2">
          <div class="font-weight-bold">Botanical Buddy</div>
          <v-chip color="grey-lighten-3" class="ml-2">
            <v-progress-circular indeterminate size="16" color="primary"></v-progress-circular> Typing...
          </v-chip>
        </div>
      </div>
    </v-card-text>
    <v-card-actions class="pa-4">
      <v-text-field
        v-model="newMessage"
        label="Ask a question"
        variant="outlined"
        ref="messageInput"
        @keydown.enter.prevent="sendMessage"
        :disabled="chatStore.loading"
        aria-label="Chat message input"
        clearable
        placeholder="e.g., Why are the leaves on my rose turning yellow?"
        class="mr-2"
      ></v-text-field>
      <v-btn
        color="primary"
        @click="sendMessage"
        :loading="chatStore.loading"
        :disabled="chatStore.loading || !newMessage.trim()"
      >
        Send
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue';
import { useChatStore } from '../stores/chatstore';
import DOMPurify from 'dompurify';
import { VCard, VCardTitle, VCardText, VCardActions, VTextField, VBtn, VChip, VProgressCircular } from 'vuetify/components';

export default {
  components: {
    VCard,
    VCardTitle,
    VCardText,
    VCardActions,
    VTextField,
    VBtn,
    VChip,
    VProgressCircular,
  },
  setup() {
    const chatStore = useChatStore();
    const newMessage = ref('');
    // Removed plantName ref
    const messageList = ref(null);
    const messageInput = ref(null);

    onMounted(() => {
      scrollToBottom();
    });

    const scrollToBottom = async () => {
      await nextTick();
      if (messageList.value) {
        messageList.value.scrollTop = messageList.value.scrollHeight;
      }
    };

    const sanitizeInput = (text) => {
      return DOMPurify.sanitize(text);
    };

    const sendMessage = async () => {
      if (!newMessage.value.trim()) return;

      const sanitizedMessage = sanitizeInput(newMessage.value);

      try {
        await chatStore.sendMessage(sanitizedMessage); // Removed plantName
        newMessage.value = '';
        scrollToBottom();
        if (messageInput.value) {
          messageInput.value.focus();
        }
      } catch (error) {
        console.error('Error sending message:', error);
        // You might want to add user-facing error feedback here, like a temporary snackbar message.
      }
    };

    return {
      chatStore,
      newMessage,
      // Removed plantName
      messageList,
      messageInput,
      sendMessage,
      scrollToBottom,
    };
  },
};
</script>

<style scoped>
/* Example styling to further refine the chat window */
.v-card-title {
  border-bottom: 1px solid rgba(0, 0, 0, 0.12);
}
</style>