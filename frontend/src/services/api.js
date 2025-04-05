import axios from 'axios';

// Create API instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    // Use a default token for demo purposes
    'Authorization': 'Bearer guest-access-token'
  },
});

// API service methods with mock data for the template
const apiService = {
  // Deadlines
  getDeadlines: async (params) => {
    // Try to get from API, but fall back to mock data
    try {
      return await api.get('/deadlines', { params });
    } catch (error) {
      console.log('Using mock data due to API error:', error);
      // Return mock data
      return {
        data: {
          deadlines: [
            {
              id: '1',
              title: 'Math Assignment #3',
              date_str: 'December 15th, 2023',
              channel_name: 'math-101',
              guild_name: 'School Server',
              timestamp: new Date().toISOString(),
            },
            {
              id: '2',
              title: 'Physics Lab Report',
              date_str: 'December 10th, 2023',
              channel_name: 'physics-202',
              guild_name: 'School Server',
              timestamp: new Date().toISOString(),
            },
            {
              id: '3',
              title: 'Term Paper Outline',
              date_str: 'December 20th, 2023',
              channel_name: 'english-comp',
              guild_name: 'School Server',
              timestamp: new Date().toISOString(),
            },
          ],
          total: 3,
          skip: 0,
          limit: 10
        }
      };
    }
  },
  
  getDeadline: async (id) => {
    // Try to get from API, but fall back to mock data
    try {
      return await api.get(`/deadlines/${id}`);
    } catch (error) {
      console.log('Using mock data due to API error:', error);
      // Return mock data for the specific ID
      return {
        data: {
          id,
          title: 'Math Assignment #3',
          date_str: 'December 15th, 2023',
          raw_content: 'Don\'t forget the Math Assignment #3 is due on December 15th. It covers chapters 7-9 and includes all practice problems at the end of each chapter.',
          channel_name: 'math-101',
          guild_name: 'School Server',
          author_name: 'Professor Smith',
          timestamp: new Date().toISOString(),
          source_link: 'https://discord.com/channels/123456789/123456789/123456789',
        }
      };
    }
  },
  
  // Auth (kept for future implementation)
  login: (credentials) => api.post('/token', credentials),
};

export default api;
export { apiService }; 