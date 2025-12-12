import React from 'react';

const Home = () => {
  return (
    <div className="container">
      <h1 style={{ textAlign: 'center', margin: '40px 0' }}>Welcome to Film Platform</h1>

      <div style={{
        maxWidth: '600px',
        margin: '0 auto',
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '30px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <p style={{ textAlign: 'center', marginBottom: '30px', fontSize: '18px' }}>
          A distributed platform for film data aggregation and analysis
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '20px',
          marginTop: '30px'
        }}>
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '20px',
            borderRadius: '6px'
          }}>
            <h3 style={{ color: '#3498db', marginBottom: '15px' }}>Features</h3>
            <ul style={{ paddingLeft: '20px', color: '#555' }}>
              <li>User Authentication</li>
              <li>Film Data Management</li>
              <li>Location Tracking</li>
              <li>Analytics Dashboard</li>
            </ul>
          </div>

          <div style={{
            backgroundColor: '#f1f8e9',
            padding: '20px',
            borderRadius: '6px'
          }}>
            <h3 style={{ color: '#27ae60', marginBottom: '15px' }}>Get Started</h3>
            <p style={{ marginBottom: '20px', color: '#555' }}>
              Register for an account or login to access the platform features.
            </p>
            <div style={{ display: 'flex', gap: '10px' }}>
              <a
                href="/register"
                className="btn btn-success"
                style={{ flex: 1, textAlign: 'center' }}
              >
                Register
              </a>
              <a
                href="/login"
                className="btn btn-primary"
                style={{ flex: 1, textAlign: 'center' }}
              >
                Login
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;