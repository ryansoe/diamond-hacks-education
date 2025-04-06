import axios from 'axios';

// Create API instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to add the token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    } else {
      // Use a default token for demo purposes when not logged in
      config.headers['Authorization'] = 'Bearer guest-access-token';
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      if (error.response.status === 401) {
        console.log('Unauthorized - Redirecting to login');
        // In a real app, you might want to redirect to login
        // or refresh the token
        localStorage.removeItem('auth_token');
      }
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // The request was made but no response was received
      console.error('Network Error:', error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

const formatDateString = (dateStr) => {
  // Remove ordinal suffixes like "st", "nd", "rd", "th"
  const cleanedDateStr = dateStr.replace(/(\d+)(st|nd|rd|th)/, '$1'); 
  const dateObj = new Date(cleanedDateStr);
  
  if (isNaN(dateObj.getTime())) {
    return null; 
  }

  const year = dateObj.getFullYear();
  const month = String(dateObj.getMonth() + 1).padStart(2, '0'); 
  const day = String(dateObj.getDate() +1).padStart(2, '0');
  
  return `${year}-${month}-${day}`;
};

// Attempt to fetch a guest token on initialization
const fetchGuestToken = async () => {
  try {
    const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/guest-token`);
    if (response.data && response.data.access_token) {
      localStorage.setItem('auth_token', response.data.access_token);
      return response.data.access_token;
    }
  } catch (error) {
    console.warn('Could not fetch guest token, falling back to public endpoints', error);
  }
  return null;
};

// Initialize guest token
fetchGuestToken();

// API service methods
const apiService = {
  // Deadlines
  getDeadlines: async (params) => {
    try {
      // Try the public endpoint first - no authentication required
      const response = await api.get('/public/deadlines', { params });
      return response;
    } catch (error) {
      console.log('Using mock data due to API error:', error);
      // Return mock data as fallback (useful for development without backend)
      return {
        data: {
          deadlines: [
            {
              id: '1',
              title: 'software engineering internship opportunity',
              date_str: 'April 15th, 2025',
              channel_name: 'math-101',
              guild_name: 'School Server',
              timestamp: formatDateString('April 15th, 2025'),
              description: 'Software engineering internship for summer 2025',
            },
            {
              id: '2',
              title: 'ACM Projects meeting',
              date_str: 'April 10th, 2025',
              channel_name: 'announcements',
              guild_name: 'ACM Club',
              timestamp: formatDateString('April 29th, 2025'),
              description: 'Weekly ACM projects meeting - all welcome!',
            },
            {
              id: '3',
              title: 'scholarship opportunity',
              date_str: 'April 20th, 2025',
              channel_name: 'english-comp',
              guild_name: 'School Server',
              timestamp: formatDateString('April 20th, 2025'),
              description: 'Scholarship application deadline approaching',
            },
            {
              id: '4',
              title: 'ACM Club Meeting',
              date_str: 'May 2nd, 2025',
              channel_name: 'announcements',
              guild_name: 'ACM UCSD',
              timestamp: formatDateString('May 2nd, 2025'),
              description: 'General body meeting with free pizza!',
            },
            {
              id: '5',
              title: 'Nursing Internship',
              date_str: 'May 2nd, 2025',
              channel_name: 'announcements',
              guild_name: 'Nursing Department',
              timestamp: formatDateString('May 2nd, 2025'),
              description: 'Summer nursing internship opportunity',
            },
          ],
          total: 5,
          skip: 0,
          limit: 10
        }
      };
    }
  },
  
  getDeadline: async (id) => {
    try {
      // Try the public endpoint first - no authentication required
      const response = await api.get(`/public/deadlines/${id}`);
      return response;
    } catch (error) {
      console.log('Using mock data due to API error:', error);
      // Return mock data for the specific ID as fallback
      return {
        data: {
          id, 
          title: 'Eventory Demo Event',
          date_str: 'April 15th, 2025',
          raw_content: 'This is a sample event from the mock data. In production, this would be real data from the API.',
          channel_name: 'announcements',
          guild_name: 'Eventory Server',
          author_name: 'Eventory Bot',
          timestamp: new Date().toISOString(),
          source_link: 'https://discord.com/channels/123456789/123456789/123456789',
          description: 'Sample event description with details about location, time, and more.',
        }
      };
    }
  },
  
  // Auth
  login: async (credentials) => {
    try {
      const response = await api.post('/token', credentials);
      // Store token in localStorage for use in future requests
      if (response.data && response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
      }
      return response;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('auth_token');
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('auth_token');
  }
};

export default api;
export { apiService }; 