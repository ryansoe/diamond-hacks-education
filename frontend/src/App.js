import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';

// Layout components
import MainLayout from './layouts/MainLayout';

// Page components
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Calendar from './pages/Calendar';
import DeadlineDetail from './pages/DeadlineDetail';
import NotFound from './pages/NotFound';
import AdminPanel from './pages/AdminPanel';

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Admin route component
const AdminRoute = ({ children }) => {
  const { isAuthenticated, isAdmin } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }
  
  return children;
};

function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />

      {/* Protected routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="calendar" element={<Calendar />} />
        <Route path="deadlines/:id" element={<DeadlineDetail />} />
        
        {/* Admin routes */}
        <Route path="admin" element={
          <AdminRoute>
            <AdminPanel />
          </AdminRoute>
        } />
      </Route>
      
      {/* 404 route */}
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}

export default App; 