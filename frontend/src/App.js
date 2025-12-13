// frontend/src/App.js - AŽURIRANO
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Navbar from './components/Navbar';
import PrivateRoute from './components/PrivateRoute';
import Home from './pages/Home';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './pages/Dashboard';
import ETLDashboard from './components/ETLDashboard'; // NOVO
import DataExplorer from './pages/DataExplorer';     // NOVO
import './index.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
          <Navbar />
          <main style={{ flex: 1, padding: '20px 0' }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route
                path="/dashboard"
                element={
                  <PrivateRoute>
                    <Dashboard />
                  </PrivateRoute>
                }
              />
              {/* NOVE RUTE */}
              <Route
                path="/etl-dashboard"
                element={
                  <PrivateRoute>
                    <ETLDashboard />
                  </PrivateRoute>
                }
              />
              <Route
                path="/data-explorer"
                element={
                  <PrivateRoute>
                    <DataExplorer />
                  </PrivateRoute>
                }
              />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
          <footer className="footer">
            <div className="container">
              <p>© 2024 Distributed Film Platform. All rights reserved.</p>
            </div>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;