// auth.js
import { defineStore } from 'pinia';
import Cookies from 'js-cookie';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null);
  const accessToken = ref(Cookies.get('access_token') || null);
  const refreshToken = ref(Cookies.get('refresh_token') || null);
  const error = ref(null);
  const loading = ref(false);

  const isAuthenticated = computed(() => !!accessToken.value);

  const login = async (username, password) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.detail || 'Login failed. Please try again.';
        throw new Error(errorMessage);
      }

      const data = await response.json();
      accessToken.value = data.access;
      refreshToken.value = data.refresh;
      Cookies.set('access_token', data.access, {
        secure: true,
        httpOnly: true,
        sameSite: 'Strict',
      });
      Cookies.set('refresh_token', data.refresh, {
        secure: true,
        httpOnly: true,
        sameSite: 'Strict',
      });

      // Fetch user details after successful login (optional)
      await fetchUser();

    } catch (err) {
      console.error('Login error:', err);
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const signup = async (username, email, password) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('/signup/', { // Adjust URL if different
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const errorMessage = errorData.detail || 'Signup failed. Please try again.';
        throw new Error(errorMessage);
      }

      // Optionally log the user in immediately after signup
      // or redirect them to the login page.
      // const loginResponse = await login(username, password);
      // if (loginResponse) {
      //   // Handle successful login after signup
      // }

      // For simplicity, we might just show a success message here
      console.log('Signup successful!');

    } catch (err) {
      console.error('Signup error:', err);
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const logout = async () => {
    const refreshTokenValue = refreshToken.value; // Store current refresh token

    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    Cookies.remove('access_token');
    Cookies.remove('refresh_token');

    // Attempt to blacklist the refresh token on the backend
    if (refreshTokenValue) {
      try {
        const response = await fetch('/logout/', { // Your logout API endpoint
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh_token: refreshTokenValue }),
        });

        if (!response.ok) {
          console.error('Error blacklisting refresh token:', response);
        }
      } catch (err) {
        console.error('Error sending logout request to backend:', err);
      }
    }
  };

  const fetchUser = async () => {
    if (isAuthenticated.value) {
      try {
        const response = await fetch('/api/users/me/', { // Adjust URL for fetching user details
          headers: {
            'Authorization': `Bearer ${accessToken.value}`,
          },
        });
        if (response.ok) {
          user.value = await response.json();
        } else {
          console.error('Failed to fetch user details');
          // Optionally handle token refresh or logout if fetching user fails
        }
      } catch (error) {
        console.error('Error fetching user details:', error);
      }
    }
  };

  // Initialize the store on load (optional - if you want to persist session across refreshes)
  const initializeStore = () => {
    accessToken.value = Cookies.get('access_token') || null;
    refreshToken.value = Cookies.get('refresh_token') || null;
    if (isAuthenticated.value) {
      fetchUser();
    }
  };
  initializeStore(); // Call it when the store is created

  return {
    user,
    accessToken,
    refreshToken,
    error,
    loading,
    isAuthenticated,
    login,
    signup,
    logout,
    fetchUser,
  };
});