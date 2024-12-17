import { defineStore } from 'pinia';
import Cookies from 'js-cookie';

export const useAuthStore = defineStore('auth', {
    /**
     * State properties:
     * - user: null, the user object associated with the user (only available when isAuthenticated is true)
     * - token: null, the access token for the authenticated user (only available when isAuthenticated is true)
     * - error: null, the error message associated with the last login attempt (only available when isAuthenticated is false)
     */
  state: () => ({
    user: null,
    token: null,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    /**
     * Attempt to log in to the application with the given username and password.
     * After a successful login, the user object and access token are stored in the state.
     * The access token is also stored in a secure cookie.
     *
     * @throws {Error} If the login attempt fails.
     *
     * @param {string} username - The username for the login attempt.
     * @param {string} password - The password for the login attempt.
     */
    async login(username, password) {
      this.error = null;
      try {
        // **Input Validation:**
        if (!username || !password) {
          throw new Error('Please enter both username and password.');
        }
        if (password.length < 8) { // Example password length validation
          throw new Error('Password must be at least 8 characters long.');
        }

        const response = await fetch('/api/login/', {
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
        this.user = data.user;
        this.token = data.token;

        // **Secure Cookie Storage:**
        Cookies.set('auth_token', this.token, {
          secure: true, // Only transmit over HTTPS (essential for production)
          httpOnly: true, // Prevent client-side JavaScript access
          sameSite: 'Strict', // Mitigate CSRF attacks
          // ... other cookie options (e.g., expires) ...
        });

      } catch (error) {
        console.error('Login error:', error);
        this.error = error.message;
      }
    },
    /**
     * Attempt to sign up a new user with the given username, email, and password.
     * After a successful signup, the error property is set to null.
     * The method throws an Error if the signup attempt fails.
     *
     * @throws {Error} If the signup attempt fails.
     *
     * @param {string} username - The username for the signup attempt.
     * @param {string} email - The email address for the signup attempt.
     * @param {string} password - The password for the signup attempt.
     */
    async signup(username, email, password) {
      this.error = null;
      try {
        // **Input Validation:**
        if (!username || !email || !password) {
          throw new Error('Please fill in all the required fields.');
        }
        if (!isValidEmail(email)) {
          throw new Error('Please enter a valid email address.');
        }
        // ... other validation rules (e.g., password complexity)

        const response = await fetch('/api/signup/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username, email, password }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          const errorMessage = errorData.detail || 'Signup failed. Please try again.';
          throw new Error(errorMessage);
        }

      } catch (error) {
        console.error('Signup error:', error);
        this.error = error.message;
      }
    },
    /**
     * Log out the current user and remove the secure cookie.
     * After a successful logout, the user and token properties are set to null.
     * The method throws an Error if the logout attempt fails.
     *
     * @throws {Error} If the logout attempt fails.
     */
    async logout() {
      try {
        await fetch('/api/logout/', { method: 'POST' });
        this.user = null;
        this.token = null;
        Cookies.remove('auth_token'); 
      } catch (error) {
        console.error('Logout error:', error);
        this.error = error.message;
      }
    },
  },
});

// Helper function for email validation
function isValidEmail(email) {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailPattern.test(email);
}