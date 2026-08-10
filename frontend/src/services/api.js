import axios from 'axios';

/**
 * PLACEHOLDER — Member 2 (Ashwini shenoy) builds the real version.
 * Expected structure (from task breakdown):
 *
 * const api = axios.create({ baseURL: 'https://your-backend-url/api' });
 *
 * api.interceptors.request.use((config) => {
 *   const token = localStorage.getItem('token');
 *   if (token) config.headers.Authorization = `Bearer ${token}`;
 *   return config;
 * });
 *
 * export default api;
 */

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
});

export default api;
