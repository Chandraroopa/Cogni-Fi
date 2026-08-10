import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext'; // Member 2 (Ashwini) builds this hook

function Navbar() {
  const { isAuthenticated, user, logout } = useAuth(); // provided by AuthContext
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();          // clears token from AuthContext / storage
    navigate('/');
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light shadow-sm px-4">
      <Link className="navbar-brand fw-bold" to="/">
        CogniFi 
      </Link>

      <div className="ms-auto d-flex align-items-center gap-3">
        <Link to="/" className="nav-link">Home</Link>

        {isAuthenticated ? (
          <>
            <Link to="/dashboard" className="nav-link">Dashboard</Link>
            <span className="text-muted small">Hi, {user?.name || 'User'}</span>
            <button className="btn btn-outline-danger btn-sm" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/signup" className="btn btn-primary btn-sm">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
