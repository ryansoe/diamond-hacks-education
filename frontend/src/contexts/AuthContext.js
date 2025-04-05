import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

// Create auth context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // Check if user is already logged in (on app load)
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      
      if (token) {
        try {
          // Set the token in axios headers
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // For the template, we'll just assume the token is valid
          // In a real app, you'd verify the token with the backend
          setIsAuthenticated(true);
          
          // Set user and admin status
          // This is a placeholder - in a real app, you'd get user info from the API
          setUser({ username: 'user' });
          setIsAdmin(localStorage.getItem('isAdmin') === 'true');
        } catch (error) {
          console.error('Error verifying auth token:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('isAdmin');
        }
      }
      
      setLoading(false);
    };
    
    checkAuth();
  }, []);
  
  // Login function
  const login = async (username, password) => {
    try {
      const response = await api.post('/token', { username, password });
      const { access_token } = response.data;
      
      // Save token to localStorage
      localStorage.setItem('token', access_token);
      
      // Set the token in axios headers
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Set authenticated state
      setIsAuthenticated(true);
      
      // Set user
      setUser({ username });
      
      // Check if admin (in a real app, this would come from the backend)
      const isAdminUser = username === 'admin';
      setIsAdmin(isAdminUser);
      localStorage.setItem('isAdmin', isAdminUser);
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };
  
  // Logout function
  const logout = () => {
    // Remove token from localStorage
    localStorage.removeItem('token');
    localStorage.removeItem('isAdmin');
    
    // Remove token from axios headers
    delete api.defaults.headers.common['Authorization'];
    
    // Reset state
    setIsAuthenticated(false);
    setUser(null);
    setIsAdmin(false);
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
      {!loading && children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
}; 