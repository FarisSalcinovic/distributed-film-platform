// frontend/src/components/ETLDashboard.js - FINALNA VERZIJA
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { etlAPI, analyticsAPI } from '../services/etlApi';
import './ETLDashboard.css';

const ETLDashboard = () => {
  const { user } = useAuth();
  const [etlStatus, setEtlStatus] = useState(null);
  const [correlationData, setCorrelationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [runningETL, setRunningETL] = useState(false);
  const [refreshTime, setRefreshTime] = useState(30);
  const [latestJobs, setLatestJobs] = useState([]);

  // Testiranje endpointa prije pokretanja
  const testEndpointsBeforeRunning = async () => {
    console.log('Testing ETL endpoints before running...');

    try {
      // Testiraj osnovne endpointove
      const statusResponse = await etlAPI.getStatus();
      console.log('✅ ETL Status endpoint works:', statusResponse.status);

      const testResponse = await etlAPI.testETLEndpoint();
      console.log('✅ ETL Test endpoint works:', testResponse.message);

      return true;
    } catch (error) {
      console.error('❌ Endpoint test failed:', error.response?.status || error.message);

      alert(
        `API endpoints not found!\n\n` +
        `Please check:\n` +
        `1. Backend is running: http://localhost:8000\n` +
        `2. Check backend logs for errors\n\n` +
        `Error: ${error.response?.status || error.message}`
      );

      return false;
    }
  };

  // Fetch all ETL data
  const fetchETLData = async () => {
    setLoading(true);
    try {
      const [statusData, jobsData] = await Promise.all([
        etlAPI.getStatus(),
        etlAPI.getLatestJobs(5)
      ]);

      setEtlStatus(statusData);
      setLatestJobs(jobsData.jobs || []);
      setError('');
    } catch (err) {
      console.error('Error fetching ETL data:', err);
      setError(`Failed to load ETL data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Run TMDB ETL
  const runTMDBETL = async () => {
    try {
      // Testiraj endpoint prije nego što pokreneš
      const endpointsWorking = await testEndpointsBeforeRunning();
      if (!endpointsWorking) {
        return;
      }

      setRunningETL(true);
      const response = await etlAPI.runTMDBETL(2, 10);
      alert(`🎬 TMDB ETL started!\n${response.message}`);

      // Start countdown and refresh
      startCountdown();
    } catch (err) {
      console.error('Error running TMDB ETL:', err);
      alert(`Failed to run TMDB ETL: ${err.response?.data?.detail || err.message}`);
      setRunningETL(false);
    }
  };

  // Run Places ETL
  const runPlacesETL = async () => {
    try {
      setRunningETL(true);
      const response = await etlAPI.runPlacesETL(['US', 'GB', 'FR'], 10);
      alert(`📍 Places ETL started!\n${response.message}`);

      startCountdown();
    } catch (err) {
      console.error('Error running Places ETL:', err);
      alert(`Failed to run Places ETL: ${err.response?.data?.detail || err.message}`);
      setRunningETL(false);
    }
  };

  // Run Full ETL
  const runFullETL = async () => {
    if (!window.confirm('Are you sure you want to run the full ETL pipeline? This may take several minutes.')) {
      return;
    }

    setRunningETL(true);
    try {
      const response = await etlAPI.runFullETL();
      alert(`🚀 Full ETL pipeline started!\n${response.message}`);

      startCountdown();
    } catch (err) {
      console.error('Error running Full ETL:', err);
      alert(`❌ Failed to run ETL pipeline: ${err.response?.data?.detail || err.message}`);
      setRunningETL(false);
    }
  };

  // Run Enrichment
  const runEnrichment = async () => {
    try {
      setRunningETL(true);
      const response = await etlAPI.runEnrichmentETL();
      alert(`🔗 Enrichment ETL started!\n${response.message}`);

      startCountdown();
    } catch (err) {
      console.error('Error running Enrichment ETL:', err);
      alert(`Failed to run Enrichment ETL: ${err.response?.data?.detail || err.message}`);
      setRunningETL(false);
    }
  };

  // Test API Connections
  const testAPIConnections = async () => {
    try {
      setRunningETL(true);
      const response = await etlAPI.testAPIConnections();
      alert(`✅ API connections tested!\nStatus: ${response.message}`);
      setRunningETL(false);
    } catch (err) {
      console.error('Error testing API connections:', err);
      alert(`Failed to test API connections: ${err.message}`);
      setRunningETL(false);
    }
  };

  // Countdown timer
  const startCountdown = () => {
    let countdown = 30;
    const countdownInterval = setInterval(() => {
      setRefreshTime(countdown);
      countdown--;

      if (countdown <= 0) {
        clearInterval(countdownInterval);
        fetchETLData();
        setRunningETL(false);
        setRefreshTime(30);
      }
    }, 1000);
  };

  // Refresh button handler
  const handleRefresh = () => {
    fetchETLData();
  };

  useEffect(() => {
    fetchETLData();

    // Auto-refresh every 60 seconds
    const interval = setInterval(fetchETLData, 60000);
    return () => clearInterval(interval);
  }, []);

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString();
    } catch (e) {
      return dateString;
    }
  };

  // Prepare chart data
  const prepareChartData = () => {
    if (!etlStatus) return [];
    // Koristi podatke iz status endpointa
    return [
      { name: 'API Status', value: etlStatus.status === 'active' ? 100 : 0, color: '#8884d8' },
      { name: 'TMDB API', value: etlStatus.apis_configured?.tmdb ? 100 : 0, color: '#82ca9d' },
      { name: 'Geoapify API', value: etlStatus.apis_configured?.geoapify ? 100 : 0, color: '#ffc658' },
      { name: 'Celery', value: etlStatus.celery_available ? 100 : 0, color: '#ff8042' }
    ];
  };

  if (loading) {
    return (
      <div className="container loading-container">
        <div className="spinner"></div>
        <p>Loading ETL Dashboard...</p>
      </div>
    );
  }

  const chartData = prepareChartData();

  return (
    <div className="etl-dashboard">
      <div className="container">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h1>🚀 ETL Dashboard</h1>
            <p className="lead">Real-time monitoring of Film & Location data pipeline</p>
            {etlStatus && (
              <span className={`status-badge ${etlStatus.status === 'active' ? 'status-ok' : 'status-warning'}`}>
                Status: {etlStatus.status}
              </span>
            )}
          </div>
          <div className="header-actions">
            <button
              className="btn btn-secondary"
              onClick={handleRefresh}
              disabled={runningETL}
            >
              🔄 Refresh
            </button>
            <button
              className="btn btn-primary"
              onClick={runFullETL}
              disabled={runningETL}
            >
              {runningETL ? (
                <>
                  <span className="spinner-small"></span>
                  Running ({refreshTime}s)
                </>
              ) : '🚀 Run Full ETL'}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="alert alert-warning">
            <strong>Note:</strong> {error}
          </div>
        )}

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">🎬</div>
            <div className="stat-content">
              <h3>{etlStatus?.apis_configured?.tmdb ? '✅' : '❌'}</h3>
              <p>TMDB API</p>
              <small>{etlStatus?.apis_configured?.tmdb ? 'Configured' : 'Not configured'}</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📍</div>
            <div className="stat-content">
              <h3>{etlStatus?.apis_configured?.geoapify ? '✅' : '❌'}</h3>
              <p>Geoapify API</p>
              <small>{etlStatus?.apis_configured?.geoapify ? 'Configured' : 'Not configured'}</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⚡</div>
            <div className="stat-content">
              <h3>{etlStatus?.celery_available ? '✅' : '❌'}</h3>
              <p>Celery Worker</p>
              <small>{etlStatus?.celery_available ? 'Running' : 'Not available'}</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔄</div>
            <div className="stat-content">
              <h3>{latestJobs.length}</h3>
              <p>Recent Jobs</p>
              <small>Last 5 jobs</small>
            </div>
          </div>
        </div>

        {/* Charts and Controls */}
        <div className="dashboard-content">
          {/* Left Column - Charts */}
          <div className="content-column">
            <div className="card">
              <div className="card-header">
                <h3>📊 System Status</h3>
              </div>
              <div className="card-body">
                <div className="chart-container">
                  {chartData.map((item, index) => (
                    <div key={index} className="chart-bar">
                      <div className="bar-label">
                        <span className="bar-name">{item.name}</span>
                        <span className="bar-value">{item.value}%</span>
                      </div>
                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${item.value}%`,
                            backgroundColor: item.color
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* System Info */}
            <div className="card">
              <div className="card-header">
                <h3>⚙️ System Info</h3>
              </div>
              <div className="card-body">
                <div className="system-info">
                  <div className="info-item">
                    <span className="info-label">Last Updated:</span>
                    <span className="info-value">{formatDate(etlStatus?.timestamp)}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">User Role:</span>
                    <span className="info-value">{user?.role || 'standard'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Backend:</span>
                    <span className="info-value">FastAPI (Python)</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Database:</span>
                    <span className="info-value">MongoDB</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Controls and Jobs */}
          <div className="content-column">
            {/* ETL Controls */}
            <div className="card">
              <div className="card-header">
                <h3>⚡ ETL Controls</h3>
              </div>
              <div className="card-body">
                <div className="etl-controls">
                  <div className="control-group">
                    <h4>🎬 TMDB ETL</h4>
                    <p>Fetch movies from TMDB database</p>
                    <button className="btn btn-outline-primary" onClick={runTMDBETL} disabled={runningETL}>
                      Run TMDB ETL
                    </button>
                  </div>

                  <div className="control-group">
                    <h4>📍 Places ETL</h4>
                    <p>Fetch places from Geoapify</p>
                    <button className="btn btn-outline-success" onClick={runPlacesETL} disabled={runningETL}>
                      Run Places ETL
                    </button>
                  </div>

                  <div className="control-group">
                    <h4>🔗 Enrichment</h4>
                    <p>Create film-location correlations</p>
                    <button className="btn btn-outline-warning" onClick={runEnrichment} disabled={runningETL}>
                      Run Enrichment
                    </button>
                  </div>

                  <div className="control-group">
                    <h4>🔌 Test APIs</h4>
                    <p>Test API connections</p>
                    <button className="btn btn-outline-info" onClick={testAPIConnections} disabled={runningETL}>
                      Test Connections
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Jobs */}
            <div className="card">
              <div className="card-header">
                <h3>📋 Recent ETL Jobs</h3>
              </div>
              <div className="card-body">
                {latestJobs.length > 0 ? (
                  <div className="jobs-list">
                    {latestJobs.map((job, index) => (
                      <div key={index} className="job-item">
                        <div className="job-header">
                          <span className="job-type">{job.job_type}</span>
                          <span className={`job-status ${job.status}`}>
                            {job.status}
                          </span>
                        </div>
                        <div className="job-details">
                          <div className="job-time">
                            <span>Started: {formatDate(job.started_at)}</span>
                            {job.completed_at && (
                              <span>Completed: {formatDate(job.completed_at)}</span>
                            )}
                          </div>
                          {job.results && (
                            <div className="job-results">
                              {job.job_type === 'tmdb' ? (
                                <>
                                  Movies: {job.results.processed || 0}
                                  {job.results.error_count > 0 && (
                                    <span className="errors"> ({job.results.error_count} errors)</span>
                                  )}
                                </>
                              ) : job.job_type === 'geoapify_places' ? (
                                <>
                                  Places: {job.results.total_processed || 0}
                                </>
                              ) : (
                                <>
                                  Processed: {job.results.processed || 0} items
                                </>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="empty-state">
                    <p>No ETL jobs found. Run an ETL pipeline to see job history.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <div className="dashboard-footer">
          <p>
            <strong>Note:</strong> This dashboard shows real-time data from your ETL pipelines.
            Run ETL jobs to populate data.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ETLDashboard;