import React, {
  createContext,
  useContext,
  useEffect,
  useState,
} from 'react';

import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check whether a user is already logged in
  useEffect(() => {
    const token =
      localStorage.getItem('token') ||
      sessionStorage.getItem('token');

    const storedUser =
      localStorage.getItem('user') ||
      sessionStorage.getItem('user');

    if (token) {
      setIsAuthenticated(true);

      if (storedUser) {
        try {
          setUser(JSON.parse(storedUser));
        } catch {
          localStorage.removeItem('user');
          sessionStorage.removeItem('user');
        }
      }
    }

    setLoading(false);
  }, []);

  // Login
  const login = async (email, password, rememberMe = false) => {
    const response = await api.post('/auth/login', {
      email,
      password,
    });

    const token = response.data?.token;
    const loggedInUser = response.data?.user;

    if (!token) {
      throw new Error('Authentication token was not returned.');
    }

    // Clear old authentication data first
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');

    // Remember Me determines where authentication is stored
    const storage = rememberMe ? localStorage : sessionStorage;

    storage.setItem('token', token);

    const currentUser = loggedInUser || {
      name: email.split('@')[0],
      email,
    };

    storage.setItem('user', JSON.stringify(currentUser));

    setUser(currentUser);
    setIsAuthenticated(true);

    return response.data;
  };

  // Logout
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');

    sessionStorage.removeItem('token');
    sessionStorage.removeItem('user');

    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook
export function useAuth() {
  return useContext(AuthContext);
}

