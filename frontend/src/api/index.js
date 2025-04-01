import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
});

// Add request interceptor for JWT token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't tried to refresh the token yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        
        // Make sure we have a refresh token
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }
        
        console.log('Attempting to refresh token...');
        
        // Use the full URL for the refresh endpoint
        const response = await axios.post(
          `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/auth/token/refresh/`, 
          { refresh: refreshToken }
        );
        
        const { access } = response.data;
        
        // Make sure we got a new access token
        if (!access) {
          throw new Error('No access token received');
        }
        
        console.log('Token refresh successful');
        localStorage.setItem('access_token', access);
        
        // Update the Authorization header for the retry
        originalRequest.headers['Authorization'] = `Bearer ${access}`;
        
        // Remove any cache-busting parameters that might cause request loops
        if (originalRequest.params && originalRequest.params.t) {
          delete originalRequest.params.t;
        }
        
        // Retry the original request with the new token
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        
        // Redirect to login if refresh fails
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        
        // Use a small timeout to allow the current request to complete
        setTimeout(() => {
          console.log('Redirecting to login page due to authentication failure');
          window.location.href = '/login';
        }, 100);
        
        return Promise.reject(refreshError);
      }
    }
    
    // For other errors, just reject the promise
    return Promise.reject(error);
  }
);

export default api;
