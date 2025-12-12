import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

const Dashboard = () => {
  const { user } = useAuth();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const data = await authAPI.getCurrentUser();
        setUserData(data);
      } catch (error) {
        console.error('Failed to fetch user data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '60px' }}>
        <div>Loading user data...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1 style={{ marginBottom: '30px' }}>Dashboard</h1>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '30px',
        marginBottom: '40px'
      }}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          padding: '25px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ color: '#3498db', marginBottom: '20px' }}>User Information</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '10px', borderBottom: '1px solid #eee' }}>
              <span style={{ fontWeight: 'bold' }}>Username:</span>
              <span>{userData?.username}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '10px', borderBottom: '1px solid #eee' }}>
              <span style={{ fontWeight: 'bold' }}>Email:</span>
              <span>{userData?.email}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '10px', borderBottom: '1px solid #eee' }}>
              <span style={{ fontWeight: 'bold' }}>Full Name:</span>
              <span>{userData?.full_name || 'Not provided'}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '10px', borderBottom: '1px solid #eee' }}>
              <span style={{ fontWeight: 'bold' }}>Role:</span>
              <span style={{ textTransform: 'capitalize' }}>{userData?.role}</span>
            </div>
          </div>
        </div>

        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          padding: '25px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ color: '#27ae60', marginBottom: '20px' }}>Quick Actions</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <button className="btn btn-primary" style={{ textAlign: 'left' }}>
              View Film Collection
            </button>
            <button className="btn btn-success" style={{ textAlign: 'left' }}>
              Import Film Data
            </button>
            <button className="btn btn-warning" style={{ textAlign: 'left', backgroundColor: '#f39c12' }}>
              Manage Account
            </button>
          </div>
        </div>
      </div>

      <div style={{
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        padding: '25px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ marginBottom: '20px' }}>Recent Activity</h2>
        <p style={{ textAlign: 'center', color: '#777', padding: '40px 0' }}>
          No recent activity. Start by exploring the platform features!
        </p>
      </div>
    </div>
  );
};

export default Dashboard;