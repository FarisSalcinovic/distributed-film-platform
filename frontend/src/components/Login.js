import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Alert from './Alert';

const Login = () => {
  const { login, error, clearError, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) clearError();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(formData.username, formData.password);
    } catch (err) {
      // Error je već postavljen u AuthContext
    }
  };

  return (
    <div className="card">
      <h2 className="text-center">Login</h2>

      {error && <Alert type="error" message={error} onClose={clearError} />}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="username">
            Username
          </label>
          <input
            className="form-input"
            id="username"
            name="username"
            type="text"
            placeholder="Enter your username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="password">
            Password
          </label>
          <input
            className="form-input"
            id="password"
            name="password"
            type="password"
            placeholder="Enter your password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>

        <button
          className={`btn btn-primary btn-block ${isLoading ? 'loading' : ''}`}
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? 'Logging in...' : 'Login'}
        </button>

        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <p>
            Don't have an account?{' '}
            <a href="/register" style={{ color: '#3498db' }}>
              Register here
            </a>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Login;