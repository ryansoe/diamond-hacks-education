import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import './App.css';

// Layout components
import MainLayout from './layouts/MainLayout';

// Page components
import Dashboard from './pages/Dashboard';
import Calendar from './pages/Calendar';
import DeadlineDetail from './pages/DeadlineDetail';
import NotFound from './pages/NotFound';
import AdminPanel from './pages/AdminPanel';

// Admin route component
const AdminRoute = ({ children }) => {
  const { isAdmin } = useAuth();
  
  // For now, we'll just render the admin component regardless
  // When you implement full authentication, you can uncomment this condition
  
  /*
  if (!isAdmin) {
    return <Navigate to="/" replace />;
  }
  */
  
  return children;
};

function App() {
  return (
    <Routes>
      {/* Main routes - no login required */}
      <Route path="/" element={<MainLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="calendar" element={<Calendar />} />
        <Route path="deadlines/:id" element={<DeadlineDetail />} />
        
        {/* Admin route - still using the AdminRoute component for future use */}
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