import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import Alert from './Alert';

const Register = () => {
  const { register, error, clearError, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  });
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    if (error) clearError();
    if (success) setSuccess(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match!');
      return;
    }

    if (formData.password.length < 8) {
      alert('Password must be at least 8 characters long!');
      return;
    }

    try {
      const { confirmPassword, ...registerData } = formData;
      await register(registerData);
      setSuccess(true);
      setFormData({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        full_name: '',
      });
    } catch (err) {
      // Error je već postavljen u AuthContext
    }
  };

  return (
    <div className="card">
      <h2 className="text-center">Register</h2>

      {error && <Alert type="error" message={error} onClose={clearError} />}
      {success && <Alert type="success" message="Registration successful! You can now login." />}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label" htmlFor="username">
            Username *
          </label>
          <input
            className="form-input"
            id="username"
            name="username"
            type="text"
            placeholder="Choose a username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="email">
            Email *
          </label>
          <input
            className="form-input"
            id="email"
            name="email"
            type="email"
            placeholder="Enter your email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="full_name">
            Full Name (Optional)
          </label>
          <input
            className="form-input"
            id="full_name"
            name="full_name"
            type="text"
            placeholder="Enter your full name"
            value={formData.full_name}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="password">
            Password *
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
          <small style={{ color: '#777', fontSize: '12px' }}>
            Must be at least 8 characters with uppercase, lowercase, and number
          </small>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="confirmPassword">
            Confirm Password *
          </label>
          <input
            className="form-input"
            id="confirmPassword"
            name="confirmPassword"
            type="password"
            placeholder="Confirm your password"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
        </div>

        <button
          className={`btn btn-success btn-block ${isLoading ? 'loading' : ''}`}
          type="submit"
          disabled={isLoading}
        >
          {isLoading ? 'Registering...' : 'Register'}
        </button>

        <div style={{ marginTop: '20px', textAlign: 'center' }}>
          <p>
            Already have an account?{' '}
            <a href="/login" style={{ color: '#3498db' }}>
              Login here
            </a>
          </p>
        </div>
      </form>
    </div>
  );
};

export default Register;