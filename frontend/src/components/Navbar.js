import React from 'react';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();

  const handleLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand">
          <a href="/" className="navbar-brand">
            Film Platform
          </a>
        </div>

        <div className="navbar-links">
          {isAuthenticated ? (
            <>
              <span style={{ marginRight: '15px' }}>Welcome, {user?.username}</span>
              <button
                onClick={handleLogout}
                className="btn btn-danger"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <a
                href="/login"
                className="btn btn-primary"
              >
                Login
              </a>
              <a
                href="/register"
                className="btn btn-success"
              >
                Register
              </a>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;