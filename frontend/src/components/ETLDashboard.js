// frontend/src/components/ETLDashboard.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './ETLDashboard.css';

const ETLDashboard = () => {
  const { user } = useAuth();
  const [etlStatus, setEtlStatus] = useState(null);
  const [correlationData, setCorrelationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [runningETL, setRunningETL] = useState(false);
  const [refreshTime, setRefreshTime] = useState(30);

  // Fetch ETL status data
  const fetchETLData = async () => {
    try {
      // Pokusaj prvo sa /api/v1/etl/status
      const statusResponse = await api.get('/api/v1/etl/status');
      setEtlStatus(statusResponse.data);

      // Pokusaj sa correlation stats
      try {
        const corrResponse = await api.get('/api/v1/etl/correlation-stats');
        setCorrelationData(corrResponse.data);
      } catch (corrErr) {
        console.log('Correlation endpoint not available:', corrErr.message);
      }

      setError('');
    } catch (err) {
      console.error('Error fetching ETL data:', err);

      // Ako endpoint ne postoji, koristi fallback podatke
      if (err.response?.status === 404) {
        setError('ETL endpoints not found. The backend might not have ETL endpoints implemented.');
        // Prikazi demo podatke
        setEtlStatus({
          status: 'demo',
          timestamp: new Date().toISOString(),
          collection_stats: {
            films: 125,
            places: 89,
            cities: 42,
            etl_jobs: 15,
            film_place_correlations: 67
          },
          last_jobs: [
            {
              job_id: 'demo-001',
              job_type: 'tmdb',
              status: 'completed',
              started_at: new Date(Date.now() - 3600000).toISOString(),
              completed_at: new Date().toISOString(),
              results: { processed: 20, errors: 0 }
            }
          ]
        });
      } else {
        setError(`Failed to load ETL data: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  // Run ETL pipeline
  const runETLPipeline = async () => {
    if (!window.confirm('Are you sure you want to run the ETL pipeline? This may take several minutes.')) {
      return;
    }

    setRunningETL(true);
    try {
      // Prvo probaj sa /api/v1/etl/run-combined
      let response;
      try {
        response = await api.post('/api/v1/etl/run-combined');
      } catch (err) {
        // Ako ne postoji, probaj sa drugim endpointom
        response = await api.post('/api/v1/etl/run-tmdb', {
          pages: 1,
          movies_per_page: 10
        });
      }

      alert(`✅ ETL pipeline started!\nTask ID: ${response.data.task_id || response.data.job_id}`);

      // Countdown timer za refresh
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

    } catch (err) {
      alert('❌ Failed to run ETL pipeline. Please check console for details.');
      console.error('ETL error:', err);
      setRunningETL(false);
    }
  };

  // Run specific TMDB ETL
  const runTMDBETL = async () => {
    try {
      const response = await api.post('/api/v1/etl/run-tmdb', {
        pages: 1,
        movies_per_page: 5
      });
      alert(`🎬 TMDB ETL started!\nTask ID: ${response.data.task_id}`);
      setTimeout(fetchETLData, 20000);
    } catch (err) {
      alert('Failed to run TMDB ETL');
    }
  };

  // Refresh button handler
  const handleRefresh = () => {
    fetchETLData();
  };

  useEffect(() => {
    fetchETLData();

    // Auto-refresh svakih 60 sekundi
    const interval = setInterval(fetchETLData, 60000);
    return () => clearInterval(interval);
  }, []);

  // Formatiranje datuma
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  // Priprema podataka za grafikon
  const prepareChartData = () => {
    if (!etlStatus) return [];
    const stats = etlStatus.collection_stats || {};
    return [
      { name: 'Movies', value: stats.films || 0, color: '#8884d8' },
      { name: 'Places', value: stats.places || 0, color: '#82ca9d' },
      { name: 'Cities', value: stats.cities || 0, color: '#ffc658' },
      { name: 'Correlations', value: stats.film_place_correlations || 0, color: '#ff8042' }
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
              <span className={`status-badge ${etlStatus.status === 'ok' ? 'status-ok' : 'status-warning'}`}>
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
              onClick={runETLPipeline}
              disabled={runningETL}
            >
              {runningETL ? (
                <>
                  <span className="spinner-small"></span>
                  Running ({refreshTime}s)
                </>
              ) : '🚀 Run ETL Pipeline'}
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
              <h3>{etlStatus?.collection_stats?.films || 0}</h3>
              <p>Movies</p>
              <small>From TMDB API</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📍</div>
            <div className="stat-content">
              <h3>{etlStatus?.collection_stats?.places || 0}</h3>
              <p>Places</p>
              <small>From Geoapify API</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔗</div>
            <div className="stat-content">
              <h3>{etlStatus?.collection_stats?.film_place_correlations || 0}</h3>
              <p>Correlations</p>
              <small>Film-Location matches</small>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔄</div>
            <div className="stat-content">
              <h3>{etlStatus?.collection_stats?.etl_jobs || 0}</h3>
              <p>ETL Jobs</p>
              <small>Completed runs</small>
            </div>
          </div>
        </div>

        {/* Charts and Controls */}
        <div className="dashboard-content">
          {/* Left Column - Charts */}
          <div className="content-column">
            <div className="card">
              <div className="card-header">
                <h3>📊 Data Distribution</h3>
              </div>
              <div className="card-body">
                <div className="chart-container">
                  {chartData.map((item, index) => (
                    <div key={index} className="chart-bar">
                      <div className="bar-label">
                        <span className="bar-name">{item.name}</span>
                        <span className="bar-value">{item.value}</span>
                      </div>
                      <div className="bar-track">
                        <div
                          className="bar-fill"
                          style={{
                            width: `${(item.value / Math.max(...chartData.map(d => d.value))) * 100}%`,
                            backgroundColor: item.color
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Correlation Stats */}
            {correlationData && correlationData.status === 'success' && (
              <div className="card">
                <div className="card-header">
                  <h3>🔗 Correlation Stats</h3>
                </div>
                <div className="card-body">
                  <div className="correlation-stats">
                    <div className="stat-number">
                      {correlationData.total_correlations || 0}
                      <span>Total Correlations</span>
                    </div>

                    {correlationData.sample_correlations && correlationData.sample_correlations.length > 0 && (
                      <div className="sample-correlations">
                        <h4>Sample Correlations:</h4>
                        {correlationData.sample_correlations.slice(0, 3).map((corr, idx) => (
                          <div key={idx} className="correlation-item">
                            <div className="film">{corr.film_title}</div>
                            <div className="arrow">→</div>
                            <div className="location">
                              📍 {corr.place_city}, {corr.place_country}
                            </div>
                            <div className="score">
                              {Math.round((corr.match_score || 0.5) * 100)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
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
                    <button className="btn btn-outline-primary" onClick={runTMDBETL}>
                      Run TMDB ETL
                    </button>
                  </div>

                  <div className="control-group">
                    <h4>📍 Geoapify ETL</h4>
                    <p>Fetch places and locations</p>
                    <button className="btn btn-outline-success" disabled>
                      Run Geoapify ETL
                    </button>
                  </div>

                  <div className="control-group">
                    <h4>🔗 Correlation</h4>
                    <p>Create film-location correlations</p>
                    <button className="btn btn-outline-warning" onClick={runETLPipeline}>
                      Run Correlation
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
                {etlStatus?.last_jobs && etlStatus.last_jobs.length > 0 ? (
                  <div className="jobs-list">
                    {etlStatus.last_jobs.slice(0, 5).map((job, index) => (
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
                              Processed: {job.results.processed || 0} items
                              {job.results.error_count > 0 && (
                                <span className="errors"> ({job.results.error_count} errors)</span>
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