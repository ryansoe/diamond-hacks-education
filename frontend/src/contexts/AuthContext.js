import React, { createContext, useState, useContext, useEffect } from 'react';
import api from '../services/api';

// Create auth context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  // Default user state - automatically authenticated
  const [user, setUser] = useState({ username: 'Guest User' });
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Auto-authenticated
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(false); // No loading since we're auto-authenticating
  
  // Set up API default headers
  useEffect(() => {
    // For API calls, we'll use a default token for now
    // In a real app, you would implement proper authentication
    const defaultToken = 'guest-access-token';
    api.defaults.headers.common['Authorization'] = `Bearer ${defaultToken}`;
  }, []);
  
  // This login function is kept for future implementation
  const login = async (username, password) => {
    // In a real implementation, you'd validate credentials with the backend
    setUser({ username });
    setIsAdmin(username === 'admin');
    return true;
  };
  
  // This logout function is kept for future implementation
  const logout = () => {
    // In a real implementation, you'd clear auth state
    setUser({ username: 'Guest User' });
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
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
}; 