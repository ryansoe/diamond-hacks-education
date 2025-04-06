import React, { createContext, useState, useContext, useEffect } from 'react';
import api, { apiService } from '../services/api';

// Create auth context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  // State for user and authentication
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Check if user is already authenticated on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem('auth_token');
      
      if (token) {
        try {
          // Set default authorization header
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Option 1: Try to fetch user profile from an endpoint (if available)
          // const response = await api.get('/me');
          // setUser(response.data);
          
          // Option 2: For demo, use the token to set basic user info
          // In production, you would use Option 1 to get real user data
          setUser({ username: 'Guest User' });
          setIsAuthenticated(true);
          setIsAdmin(false); // Set based on user role from backend
        } catch (error) {
          console.error('Auth verification failed:', error);
          localStorage.removeItem('auth_token');
          setUser(null);
          setIsAuthenticated(false);
          setIsAdmin(false);
        }
      } else {
        // Set guest credentials for demo purposes
        setUser({ username: 'Guest User' });
        setIsAuthenticated(true); // Auto-authenticate for demo
      }
      
      setLoading(false);
    };
    
    checkAuthStatus();
  }, []);
  
  // Login function
  const login = async (username, password) => {
    try {
      setLoading(true);
      const response = await apiService.login({ username, password });
      
      if (response.data.access_token) {
        // Set user after successful login
        setUser({ username });
        setIsAuthenticated(true);
        setIsAdmin(username === 'admin'); // Set admin status based on username or role
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };
  
  // Logout function
  const logout = () => {
    apiService.logout();
    setUser(null);
    setIsAuthenticated(false);
    setIsAdmin(false);
    // For demo purposes, we'll set the guest user automatically
    setUser({ username: 'Guest User' });
    setIsAuthenticated(true);
  };
  
  // Context value
  const value = {
    user,
    isAuthenticated,
    isAdmin,
    loading,
    login,
    logout
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
}; 