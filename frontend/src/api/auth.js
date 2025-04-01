import api from './index';

/**
 * Login with username and password
 * @param {string} username - User's username
 * @param {string} password - User's password
 * @returns {Promise} - API response with tokens and user data
 */
export const login = (username, password) => {
  return api.post('/api/auth/login/', { username, password });
};

/**
 * Register a new user
 * @param {Object} userData - User registration data
 * @param {string} userData.username - Username
 * @param {string} userData.password - Password
 * @param {string} userData.email - Email (optional)
 * @returns {Promise} - API response with the created user
 */
export const register = (userData) => {
  return api.post('/api/auth/register/', userData);
};

/**
 * Store authentication tokens in localStorage
 * @param {Object} tokens - Authentication tokens
 * @param {string} tokens.access - Access token
 * @param {string} tokens.refresh - Refresh token
 */
export const setAuthTokens = (tokens) => {
  localStorage.setItem('access_token', tokens.access);
  localStorage.setItem('refresh_token', tokens.refresh);
};

/**
 * Remove authentication tokens from localStorage
 */
export const clearAuthTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

/**
 * Check if user is authenticated
 * @returns {boolean} - True if user has an access token
 */
export const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

/**
 * Refresh the access token using the refresh token
 * @returns {Promise} - API response with new access token
 */
export const refreshAccessToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    throw new Error('No refresh token found');
  }
  const response = await api.post('/api/auth/refresh/', { refresh: refreshToken });
  setAuthTokens(response.data); // Store new tokens
  return response.data.access; // Return new access token
};
