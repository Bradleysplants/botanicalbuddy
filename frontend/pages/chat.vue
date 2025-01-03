<template>
  <v-container fluid>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6" lg="5">
        <v-card>
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Chat with Botanical Buddy</v-toolbar-title>
          </v-toolbar>
          <ChatWindow />
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ChatWindow from '../components/ChatWindow.vue';

export default {
  components: {
    ChatWindow,
  },
};
</script>

<style scoped>
/* You can add any specific styling for the Chat page layout here */
</style>