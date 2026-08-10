import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext'; // Member 2 (Ashwini) builds this hook

// Wraps any page that should only be visible to logged-in users.
// Usage in App.jsx:
//   <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
function ProtectedRoute({ children }) {
  // useAuth() should return something like: { isAuthenticated, user, loading }
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
