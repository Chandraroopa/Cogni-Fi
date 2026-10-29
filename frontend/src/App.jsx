
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import { AuthProvider } from './context/AuthContext';

import ProtectedRoute from './components/common/ProtectedRoute';
import CursorGlow from './components/common/CursorGlow';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';

import Home from './components/pages/Home';
import Login from './components/pages/Login';
import SignUp from './components/pages/SignUp';
import Dashboard from './components/pages/Dashboard';
import WifiScan from './components/pages/WifiScan';
import NetworkAnalysis from './components/pages/NetworkAnalysis';
import History from './components/pages/History';
import Alerts from './components/pages/Alerts';

import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-black bg-cover bg-center bg-fixed">
          <CursorGlow />

          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />

            {/* Protected dashboard */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <>
                    <Navbar />
                    <Dashboard />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            {/* Protected Wi-Fi scan */}
            <Route
              path="/wifi-scan"
              element={
                <ProtectedRoute>
                  <WifiScan />
                </ProtectedRoute>
              }
            />

            {/* Protected network analysis */}
            <Route
              path="/network-analysis"
              element={
                <ProtectedRoute>
                  <NetworkAnalysis />
                </ProtectedRoute>
              }
            />

            {/* Protected history */}
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <>
                    <Navbar />
                    <History />
                    <Footer />
                  </>
                </ProtectedRoute>
              }
            />

            {/* Protected alerts */}
            <Route
              path="/alerts"
              element={
                <ProtectedRoute>
                  <>
                    <Navbar />
                    <Alerts />
                    <Footer />
                  </>
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
