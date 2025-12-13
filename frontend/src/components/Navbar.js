// frontend/src/components/Navbar.js - AŽURIRANO
import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import './Navbar.css'; // Kreirajte ovaj CSS fajl

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
          <Link to="/" className="navbar-logo">
            🎬 Film Platform
          </Link>
        </div>

        <div className="navbar-menu">
          {isAuthenticated ? (
            <>
              <div className="navbar-links">
                <Link to="/dashboard" className="nav-link">
                  Dashboard
                </Link>
                <Link to="/etl-dashboard" className="nav-link">
                  🚀 ETL Dashboard
                </Link>
                <Link to="/data-explorer" className="nav-link">
                  🔍 Data Explorer
                </Link>
              </div>
              <div className="navbar-user">
                <span className="welcome-text">
                  Welcome, <strong>{user?.username}</strong>
                </span>
                <button
                  onClick={handleLogout}
                  className="btn btn-logout"
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <div className="navbar-auth">
              <Link to="/login" className="btn btn-login">
                Login
              </Link>
              <Link to="/register" className="btn btn-register">
                Register
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;