<template>
  <v-app>
    <v-main>
      <v-container fluid>
        <v-row align="center" justify="center">
          <v-col cols="12" sm="8" md="6" lg="4" xl="3">
            <v-card class="elevation-12">
              <v-toolbar color="green" dark flat>
                <v-toolbar-title>Botanical Buddy</v-toolbar-title>
              </v-toolbar>
              <v-card-text>
                <v-row align="center" justify="center">
                  <v-col cols="12" sm="12" md="12" lg="12" xl="12">
                    <h1 class="text-center">Welcome to Botanical Buddy</h1>
                  </v-col>
                </v-row>
                <v-row align="center" justify="center">
                  <v-col cols="12" sm="12" md="12" lg="12" xl="12">
                    <v-img src="https://source.unsplash.com/1600x900/?plants" max-height="300" contain></v-img>
                  </v-col>
                </v-row>
                <v-row align="center" justify="center">
                  <v-col cols="12" sm="12" md="12" lg="12" xl="12">
                    <p class="text-center">Botanical Buddy is your one-stop-shop for plant advice. Whether you're a seasoned gardener or just starting out, we've got you covered.</p>
                  </v-col>
                </v-row>
                <v-row align="center" justify="center">
                  <v-col cols="12" sm="12" md="12" lg="12" xl="12">
                    <v-btn color="green" dark @click="$router.push('/Chat')">Chat with our Ai</v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { useAuthStore } from '../stores/auth';

export default {
  data() {
    return {
    };
  },

  setup() {
    const authStore = useAuthStore();

    if (authStore.isAuthenticated) {
      // Handle the case when the user is already authenticated
    }

    return {
      authStore,
    };
  },
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