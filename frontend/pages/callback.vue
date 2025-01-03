<template>
  <div>
    <p>Processing authentication...</p>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

const { status } = useAuth();
const router = useRouter();

onMounted(() => {
  // You might want to add a check here to redirect if the user is already authenticated
  if (status.value === 'authenticated') {
    router.push('/'); // Redirect to homepage or dashboard
  }
});

watch(status, (newStatus) => {
  if (newStatus === 'authenticated') {
    router.push('/'); // Redirect after authentication is complete
  } else if (newStatus === 'unauthenticated' && newStatus !== 'loading') {
    // Handle potential errors or redirect to login
    console.error("Authentication failed or was interrupted.");
    router.push('/login');
  }
});
</script>