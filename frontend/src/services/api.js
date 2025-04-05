import axios from 'axios';

// Create API instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add token from local storage if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle 401 Unauthorized errors
    if (error.response && error.response.status === 401) {
      // Clear local storage and redirect to login
      localStorage.removeItem('token');
      localStorage.removeItem('isAdmin');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API service methods
const apiService = {
  // Deadlines
  getDeadlines: (params) => api.get('/deadlines', { params }),
  getDeadline: (id) => api.get(`/deadlines/${id}`),
  
  // Auth
  login: (credentials) => api.post('/token', credentials),
};

export default api;
export { apiService }; 