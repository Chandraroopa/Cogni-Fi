import React, { createContext, useContext, useState } from 'react';

/**
 * PLACEHOLDER — Member 2 (Ashwini shenoy) builds the real version.
 * Expected structure (from task breakdown):
 *
 * - login(email, password): calls api.js, stores JWT in localStorage,
 *   sets isAuthenticated + user state.
 * - logout(): clears token, resets state.
 * - On mount, check localStorage for an existing token to persist login
 *   across page refreshes.
 *
 * Everything below is a minimal working stub so Home.jsx / Navbar.jsx /
 * ProtectedRoute.jsx compile and run before the real logic is added.
 */

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  // TODO (Member 2): replace with real API call via services/api.js
  const login = async (email, password) => {
    setUser({ name: email.split('@')[0] });
    setIsAuthenticated(true);
  };

  const logout = () => {
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
