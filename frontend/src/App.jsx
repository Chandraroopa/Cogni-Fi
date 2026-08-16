import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';
import ProtectedRoute from './components/common/ProtectedRoute';

import Home from './components/pages/Home';
import Login from './components/pages/Login';
import SignUp from './components/pages/SignUp';
import Dashboard from './components/pages/Dashboard';
import WifiScan from './components/pages/WifiScan';
import NetworkAnalysis from './components/pages/NetworkAnalysis';
import { AuthProvider } from './context/AuthContext';

import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div
          className="min-h-screen bg-black bg-cover bg-center bg-fixed"
          style={{
            backgroundImage:
              "url('https://raw.githubusercontent.com/prebuiltui/prebuiltui/refs/heads/main/assets/hero/bg-gradient-2.png')",
          }}
        >

          <Routes>

            <Route
              path="/"
              element={
                <>
                  <Navbar />
                  <Home />
                  <Footer />
                </>
              }
            />

            <Route
              path="/login"
              element={
                <>
                  <Navbar />
                  <Login />
                  <Footer />
                </>
              }
            />

            <Route
              path="/signup"
              element={
                <>
                  <Navbar />
                  <SignUp />
                  <Footer />
                </>
              }
            />

<<<<<<< HEAD
           // Change it to this:
<Route path="/dashboard" element={<Dashboard />} />
=======
            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/network-analysis"
              element={<NetworkAnalysis />}
            />
            <Route
              path="/wifi-scan"
              element={<WifiScan />}
            />
>>>>>>> 97d4a63cd42c9ed0e0b48932c88bf1f975afecda
          </Routes>

          

        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;