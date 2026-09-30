<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-model="query"
          label="Ask about a plant"
          @keyup.enter="askQuestion"
        ></v-text-field>
      </v-col>
      <v-col cols="12">
        <v-btn @click="askQuestion" color="primary">Ask</v-btn>
      </v-col>
      <v-col cols="12">
        <div v-if="response">
          <h3>Response:</h3>
          <p>{{ response }}</p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      query: '',
      response: ''
    };
  },
  methods: {
    async askQuestion() {
      try {
        const response = await fetch('/api/ask_botanist/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCookie('csrftoken') 
          },
          body: JSON.stringify({ query: this.query })
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();
        this.response = data.response;
      } catch (error) {
        console.error('Error:', error);
        this.response = 'An error occurred while fetching the response.';
      }
    },
    getCookie(name) {
      let cookieValue = null;
      if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            break;
          }
        }
      }
      return cookieValue;
    }
  }
};
</script>

<style scoped>
.v-card {
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.v-toolbar {
  border-top-left-radius: 10px;
  border-top-right-radius: 10px;
}

.v-card-text {
  padding: 20px;
}

.v-row {
  margin-bottom: 20px;
}

.v-col {
  padding: 10px;
}

.v-btn {
  margin: center;
  
}

.v-img {
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
</style>