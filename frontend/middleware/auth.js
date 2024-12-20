// middleware/auth.js
export default defineNuxtRouteMiddleware((to, from) => {
    const { $auth } = useNuxtApp();
  
    // Check if the user is authenticated
    if (!$auth.isAuthenticated) {
      // Redirect to the login page if not authenticated
      return navigateTo('/login'); 
    }
  });