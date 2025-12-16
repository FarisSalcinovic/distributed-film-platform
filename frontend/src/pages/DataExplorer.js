// frontend/src/pages/DataExplorer.js - ISPRAVLJENO
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { analyticsAPI, filmLocationsAPI, etlAPI } from '../services/etlApi';
import './DataExplorer.css';

const DataExplorer = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('movies');
  const [movies, setMovies] = useState([]);
  const [places, setPlaces] = useState([]);
  const [correlations, setCorrelations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stats, setStats] = useState({
    totalMovies: 0,
    totalPlaces: 0,
    totalCorrelations: 0
  });
  const [filters, setFilters] = useState({
    country: '',
    genre: '',
    year: ''
  });

  // Demo data za fallback
  const demoMovies = [
    {
      film_id: 1,
      title: 'Inception',
      release_date: '2010-07-16',
      genres: ['Action', 'Sci-Fi', 'Thriller'],
      production_countries: ['USA', 'UK'],
      popularity: 100.5,
      vote_average: 8.8,
      locations: [
        { city_name: 'Los Angeles', country: 'USA', confidence: 0.9 },
        { city_name: 'London', country: 'UK', confidence: 0.8 }
      ],
      locations_count: 2
    },
    {
      film_id: 2,
      title: 'The Shawshank Redemption',
      release_date: '1994-09-23',
      genres: ['Drama'],
      production_countries: ['USA'],
      popularity: 85.2,
      vote_average: 9.3,
      locations: [
        { city_name: 'Mansfield', country: 'USA', confidence: 0.95 }
      ],
      locations_count: 1
    },
    {
      film_id: 3,
      title: 'The Dark Knight',
      release_date: '2008-07-18',
      genres: ['Action', 'Crime', 'Drama'],
      production_countries: ['USA', 'UK'],
      popularity: 120.7,
      vote_average: 9.0,
      locations: [
        { city_name: 'Chicago', country: 'USA', confidence: 0.85 },
        { city_name: 'London', country: 'UK', confidence: 0.75 }
      ],
      locations_count: 2
    }
  ];

  const demoPlaces = [
    {
      city_id: 1,
      name: 'Los Angeles',
      country: 'USA',
      country_code: 'US',
      population: 3980000,
      latitude: 34.0522,
      longitude: -118.2437,
      film_count: 25,
      sample_films: ['Inception', 'La La Land', 'Once Upon a Time in Hollywood']
    },
    {
      city_id: 2,
      name: 'London',
      country: 'United Kingdom',
      country_code: 'GB',
      population: 8982000,
      latitude: 51.5074,
      longitude: -0.1278,
      film_count: 18,
      sample_films: ['Harry Potter', 'James Bond', 'Sherlock Holmes']
    },
    {
      city_id: 3,
      name: 'Paris',
      country: 'France',
      country_code: 'FR',
      population: 2148000,
      latitude: 48.8566,
      longitude: 2.3522,
      film_count: 12,
      sample_films: ['Amélie', 'The Da Vinci Code', 'Midnight in Paris']
    }
  ];

  const demoCorrelations = [
    {
      film_id: 1,
      film_title: 'Inception',
      film_genres: ['Action', 'Sci-Fi'],
      suggested_locations: [
        {
          place: {
            name: 'Los Angeles',
            city: 'Los Angeles',
            country_code: 'US',
            categories: ['entertainment', 'cinema']
          },
          match_score: 0.85,
          match_reasons: ['Sci-Fi theme matches tech hubs']
        },
        {
          place: {
            name: 'Tokyo',
            city: 'Tokyo',
            country_code: 'JP',
            categories: ['tech', 'futuristic']
          },
          match_score: 0.78,
          match_reasons: ['Futuristic architecture matches film concept']
        }
      ]
    },
    {
      film_id: 3,
      film_title: 'The Dark Knight',
      film_genres: ['Action', 'Crime', 'Drama'],
      suggested_locations: [
        {
          place: {
            name: 'Chicago',
            city: 'Chicago',
            country_code: 'US',
            categories: ['urban', 'architecture']
          },
          match_score: 0.92,
          match_reasons: ['Gothic architecture matches film mood', 'Urban setting']
        }
      ]
    }
  ];

  // Fetch data based on active tab
  const fetchData = async () => {
    setLoading(true);
    try {
      // Get stats from ETL API
      const statusData = await etlAPI.getStatus();
      const statsData = statusData.collection_stats || {};
      setStats({
        totalMovies: statsData.films || 0,
        totalPlaces: statsData.places || 0,
        totalCorrelations: statsData.film_place_correlations || 0
      });

      // Fetch data based on active tab
      if (activeTab === 'movies') {
        try {
          const moviesData = await analyticsAPI.getFilmsWithLocations(20, 0, {
            country: filters.country,
            genre: filters.genre,
            year: filters.year
          });
          setMovies(moviesData.films || demoMovies);
        } catch (movieError) {
          console.log('Using demo movies data due to API error:', movieError);
          setMovies(demoMovies);
        }
      } else if (activeTab === 'places') {
        try {
          const placesData = await analyticsAPI.getPopularCities(20, 0, filters.country);
          setPlaces(placesData.cities || demoPlaces);
        } catch (placeError) {
          console.log('Using demo places data due to API error:', placeError);
          setPlaces(demoPlaces);
        }
      } else if (activeTab === 'correlations') {
        try {
          const corrData = await analyticsAPI.getFilmLocationCorrelations({
            genre: filters.genre,
            country_code: filters.country
          });
          setCorrelations(corrData.correlations || demoCorrelations);
        } catch (corrError) {
          console.log('Using demo correlations data due to API error:', corrError);
          setCorrelations(demoCorrelations);
        }
      }

    } catch (err) {
      console.error('Error fetching data:', err);
      // Use demo data as fallback
      if (activeTab === 'movies') {
        setMovies(demoMovies);
      } else if (activeTab === 'places') {
        setPlaces(demoPlaces);
      } else if (activeTab === 'correlations') {
        setCorrelations(demoCorrelations);
      }
    } finally {
      setLoading(false);
    }
  };

  // Apply filters
  const applyFilters = () => {
    fetchData();
  };

  // Clear filters
  const clearFilters = () => {
    setFilters({
      country: '',
      genre: '',
      year: ''
    });
    setSearchTerm('');
  };

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  // Filter functions
  const filteredMovies = movies.filter(movie =>
    movie.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    movie.genres?.some(genre => genre.toLowerCase().includes(searchTerm.toLowerCase())) ||
    movie.production_countries?.some(country => country.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const filteredPlaces = places.filter(place =>
    place.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    place.country.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredCorrelations = correlations.filter(corr =>
    corr.film_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    corr.film_genres?.some(genre => genre.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Get badge color based on score
  const getScoreColor = (score) => {
    if (score >= 0.8) return 'high-score';
    if (score >= 0.6) return 'medium-score';
    return 'low-score';
  };

  if (loading) {
    return (
      <div className="container loading-container">
        <div className="spinner"></div>
        <p>Loading data...</p>
      </div>
    );
  }

  return (
    <div className="data-explorer">
      <div className="container">
        {/* Header */}
        <div className="explorer-header">
          <div>
            <h1>🔍 Data Explorer</h1>
            <p className="lead">Explore and analyze film and location data</p>
          </div>
          <div className="header-stats">
            <div className="stat-badge">
              <span className="stat-number">{stats.totalMovies}</span>
              <span className="stat-label">Movies</span>
            </div>
            <div className="stat-badge">
              <span className="stat-number">{stats.totalPlaces}</span>
              <span className="stat-label">Places</span>
            </div>
            <div className="stat-badge">
              <span className="stat-number">{stats.totalCorrelations}</span>
              <span className="stat-label">Correlations</span>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="search-container">
          <div className="search-box">
            <input
              type="text"
              placeholder="Search movies, places, genres, locations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <button className="search-btn" onClick={fetchData}>
              🔍 Search
            </button>
          </div>

          <div className="filters">
            <div className="filter-group">
              <input
                type="text"
                placeholder="Country"
                value={filters.country}
                onChange={(e) => setFilters({...filters, country: e.target.value})}
                className="filter-input"
              />
            </div>
            <div className="filter-group">
              <input
                type="text"
                placeholder="Genre"
                value={filters.genre}
                onChange={(e) => setFilters({...filters, genre: e.target.value})}
                className="filter-input"
              />
            </div>
            <div className="filter-group">
              <input
                type="number"
                placeholder="Year"
                value={filters.year}
                onChange={(e) => setFilters({...filters, year: e.target.value})}
                className="filter-input"
                min="1900"
                max="2025"
              />
            </div>
            <button className="btn btn-primary" onClick={applyFilters}>
              Apply Filters
            </button>
            <button className="btn btn-secondary" onClick={clearFilters}>
              Clear
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="tabs-container">
          <div className="tabs">
            <button
              className={`tab ${activeTab === 'movies' ? 'active' : ''}`}
              onClick={() => setActiveTab('movies')}
            >
              🎬 Movies ({movies.length})
            </button>
            <button
              className={`tab ${activeTab === 'places' ? 'active' : ''}`}
              onClick={() => setActiveTab('places')}
            >
              📍 Places ({places.length})
            </button>
            <button
              className={`tab ${activeTab === 'correlations' ? 'active' : ''}`}
              onClick={() => setActiveTab('correlations')}
            >
              🔗 Correlations ({correlations.length})
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="content-area">
          {activeTab === 'movies' && (
            <div className="movies-grid">
              {filteredMovies.length > 0 ? (
                filteredMovies.map(movie => (
                  <div key={movie.film_id || movie.id} className="movie-card">
                    <div className="movie-header">
                      <h3>{movie.title}</h3>
                      <span className="movie-year">({movie.release_date?.substring(0, 4) || 'N/A'})</span>
                    </div>
                    <div className="movie-rating">
                      ⭐ {movie.vote_average?.toFixed(1) || 'N/A'}/10
                      {movie.popularity && (
                        <span className="popularity">🔥 {movie.popularity?.toFixed(0)}</span>
                      )}
                    </div>
                    <div className="movie-genres">
                      {movie.genres?.map(genre => (
                        <span key={genre} className="genre-tag">
                          {genre}
                        </span>
                      )) || <span className="genre-tag">Unknown Genre</span>}
                    </div>
                    <div className="movie-countries">
                      <strong>Countries:</strong> {movie.production_countries?.join(', ') || 'N/A'}
                    </div>
                    <div className="movie-locations">
                      <strong>Locations:</strong> {movie.locations_count || 0} found
                      {movie.locations?.slice(0, 2).map((loc, idx) => (
                        <div key={idx} className="location-tag">
                          📍 {loc.city_name}, {loc.country}
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>No movies found. Try running TMDB ETL first or adjust your filters.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'places' && (
            <div className="places-grid">
              {filteredPlaces.length > 0 ? (
                filteredPlaces.map(place => (
                  <div key={place.city_id || place.id} className="place-card">
                    <div className="place-header">
                      <h3>📍 {place.name}</h3>
                      <span className="place-country">{place.country} ({place.country_code})</span>
                    </div>
                    <div className="place-info">
                      <div className="info-item">
                        <span className="info-label">Population:</span>
                        <span className="info-value">
                          {place.population?.toLocaleString() || 'N/A'}
                        </span>
                      </div>
                      <div className="info-item">
                        <span className="info-label">Films:</span>
                        <span className="info-value">{place.film_count || 0}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-label">Coordinates:</span>
                        <span className="info-value">
                          {place.latitude?.toFixed(4) || 'N/A'}, {place.longitude?.toFixed(4) || 'N/A'}
                        </span>
                      </div>
                    </div>
                    {place.sample_films && place.sample_films.length > 0 && (
                      <div className="sample-films">
                        <strong>Sample films:</strong>
                        <div className="film-tags">
                          {place.sample_films.map((film, idx) => (
                            <span key={idx} className="film-tag">
                              🎬 {film}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>No places found. Try running Geoapify ETL first or adjust your filters.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'correlations' && (
            <div className="correlations-list">
              {filteredCorrelations.length > 0 ? (
                filteredCorrelations.map((corr, idx) => (
                  <div key={corr.film_id || idx} className="correlation-card">
                    <div className="correlation-content">
                      <div className="correlation-item movie-item">
                        <div className="item-icon">🎬</div>
                        <div className="item-details">
                          <h4>{corr.film_title}</h4>
                          <div className="genres">
                            {corr.film_genres?.map(genre => (
                              <span key={genre} className="genre-tag small">{genre}</span>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="correlation-connection">
                        <div className="connection-arrow">⇄</div>
                      </div>

                      <div className="correlation-item place-item">
                        <div className="item-icon">📍</div>
                        <div className="item-details">
                          {corr.suggested_locations && corr.suggested_locations.length > 0 ? (
                            corr.suggested_locations.slice(0, 2).map((loc, locIdx) => (
                              <div key={locIdx} className="location-detail">
                                <h4>{loc.place?.name || 'Unknown Location'}</h4>
                                <div className="location-info">
                                  {loc.place?.city}, {loc.place?.country_code}
                                  {loc.match_score && (
                                    <span className={`score-badge ${getScoreColor(loc.match_score)}`}>
                                      {Math.round(loc.match_score * 100)}%
                                    </span>
                                  )}
                                </div>
                              </div>
                            ))
                          ) : (
                            <h4>No locations matched</h4>
                          )}
                        </div>
                      </div>
                    </div>

                    {corr.suggested_locations && corr.suggested_locations[0]?.match_reasons && (
                      <div className="correlation-reason">
                        <p><strong>Match Reasons:</strong> {corr.suggested_locations[0].match_reasons.join(', ')}</p>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>No correlations found. Run enrichment ETL to create film-location matches.</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Help Section */}
        <div className="help-section">
          <div className="help-card">
            <h3>💡 How to Use Data Explorer</h3>
            <div className="help-tips">
              <div className="tip">
                <strong>Search:</strong> Use the search bar to find specific movies, places, or correlations.
              </div>
              <div className="tip">
                <strong>Filters:</strong> Apply country, genre, or year filters to narrow down results.
              </div>
              <div className="tip">
                <strong>Tabs:</strong> Switch between Movies, Places, and Correlations tabs.
              </div>
              <div className="tip">
                <strong>Data Sources:</strong> Data comes from TMDB (movies) and Geoapify (places) APIs.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataExplorer;