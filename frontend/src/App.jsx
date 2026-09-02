import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/common/ProtectedRoute';
import CursorGlow from './components/common/CursorGlow';
import Home from './components/pages/Home';
import Login from './components/pages/Login';
import SignUp from './components/pages/SignUp';
import Dashboard from './components/pages/Dashboard';
import WifiScan from './components/pages/WifiScan';
import NetworkAnalysis from './components/pages/NetworkAnalysis';

import { AuthProvider } from './context/AuthContext';

import './App.css';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-black bg-cover bg-center bg-fixed">
          <CursorGlow />

          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Navbar />
                  <Dashboard />
                  <Footer />
                </ProtectedRoute>
              }
            />

            <Route
              path="/wifi-scan"
              element={
                <ProtectedRoute>
                  <WifiScan />
                </ProtectedRoute>
              }
            />

            <Route
              path="/network-analysis"
              element={
                <ProtectedRoute>
                  <NetworkAnalysis />
                </ProtectedRoute>
              }
            />
          </Routes>

        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;