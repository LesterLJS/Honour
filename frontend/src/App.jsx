import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ImageProvider } from './context/ImageContext';


// Import pages
import Login from './pages/Login';
import Register from './pages/Register';
import ImageUpload from './pages/ImageUpload';

import AdminDashboard from './pages/Admin/Dashboard';

// Protected route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

// Admin route component
const AdminRoute = ({ children }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!isAdmin()) {
    return <Navigate to="/upload" />;
  }
  
  return children;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <ImageProvider>
          
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route 
                path="/upload" 
                element={
                  <ProtectedRoute>
                    <ImageUpload />
                  </ProtectedRoute>
                } 
              />
              
              
              
              {/* Admin routes */}
              <Route 
                path="/admin" 
                element={
                  <AdminRoute>
                    <AdminDashboard />
                  </AdminRoute>
                } 
              />
              
              {/* Redirect root to upload page */}
              <Route 
                path="/" 
                element={<Navigate to="/upload" />} 
              />
              
              {/* Catch all - redirect to upload page */}
              <Route 
                path="*" 
                element={<Navigate to="/upload" />} 
              />
            </Routes>
          
        </ImageProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
