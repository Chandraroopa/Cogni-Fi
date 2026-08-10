import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';
import ProtectedRoute from './components/common/ProtectedRoute';

import Home from './components/pages/Home';
import Login from './components/pages/Login';       // Member 2 (Ashwini) builds this
import SignUp from './components/pages/SignUp';     // Member 3 (Bhoomika) builds this
import Dashboard from './components/pages/Dashboard'; // Member 4 (Chandraroopa) builds this

import { AuthProvider } from './context/AuthContext'; // Member 2 (Ashwini) builds this

import './App.css';

function App() {
  return (
    // AuthProvider wraps the whole app so login state is available everywhere
    <AuthProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<SignUp />} />

          {/* Protected route - only accessible if logged in */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
        <Footer />
      </Router>
    </AuthProvider>
  );
}

export default App;
