// frontend/src/services/etlApi.js
import api from './api';

// ETL API Services - ISPRAVLJENI ENDPOINTI
export const etlAPI = {
  // Get ETL system status
  getStatus: async () => {
    try {
      const response = await api.get('/api/v1/etl/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching ETL status:', error);
      return {
        status: 'error',
        message: 'Failed to fetch ETL status',
        collection_stats: {},
        last_jobs: []
      };
    }
  },

  // Get correlation stats - DODAJ OVAJ ENDPOINT U etl.py AKO NE POSTOJI
  getCorrelationStats: async () => {
    try {
      const response = await api.get('/api/v1/etl/correlation-stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching correlation stats:', error);
      return {
        status: 'no_data',
        message: 'No correlation data available',
        total_correlations: 0,
        sample_correlations: []
      };
    }
  },

  // Run TMDB ETL
  runTMDBETL: async (pages = 3, movies_per_page = 20) => {
    try {
      const response = await api.post('/api/v1/etl/run-tmdb-etl', {
        pages,
        movies_per_page
      });
      return response.data;
    } catch (error) {
      console.error('Error running TMDB ETL:', error);
      throw error;
    }
  },

  // Run Places ETL - IME ENDPOINTA JE run-places-etl (NE run-geodb-etl)
  runPlacesETL: async (country_codes = ['US', 'GB', 'FR'], limit_per_country = 20) => {
    try {
      const response = await api.post('/api/v1/etl/run-places-etl', {
        country_codes,
        limit_per_country
      });
      return response.data;
    } catch (error) {
      console.error('Error running Places ETL:', error);
      throw error;
    }
  },

  // Run Enrichment
  runEnrichmentETL: async () => {
    try {
      const response = await api.post('/api/v1/etl/run-enrichment');
      return response.data;
    } catch (error) {
      console.error('Error running Enrichment ETL:', error);
      throw error;
    }
  },

  // Run Full ETL
  runFullETL: async () => {
    try {
      const response = await api.post('/api/v1/etl/run-full-etl');
      return response.data;
    } catch (error) {
      console.error('Error running Full ETL:', error);
      throw error;
    }
  },

  // Test API Connections - POST metoda
  testAPIConnections: async () => {
    try {
      const response = await api.post('/api/v1/etl/test-api-connections');
      return response.data;
    } catch (error) {
      console.error('Error testing API connections:', error);
      throw error;
    }
  },

  // Get latest jobs
  getLatestJobs: async (limit = 10) => {
    try {
      const response = await api.get('/api/v1/etl/jobs/latest', {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching latest jobs:', error);
      return {
        total_jobs: 0,
        jobs: []
      };
    }
  },

  // Test ETL endpoint (GET /test)
  testETLEndpoint: async () => {
    try {
      const response = await api.get('/api/v1/etl/test');
      return response.data;
    } catch (error) {
      console.error('Error testing ETL endpoint:', error);
      throw error;
    }
  }
};

// Analytics API Services - ISPRAVLJENI PREFIXI
export const analyticsAPI = {
  // U main.py piše: GET /api/v1/films/locations
  getFilmsWithLocations: async (limit = 50, skip = 0, filters = {}) => {
    try {
      const params = { limit, skip, ...filters };
      const response = await api.get('/api/v1/films/locations', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching films with locations:', error);
      return {
        total: 0,
        films: [],
        filters: filters
      };
    }
  },

  // U main.py piše: GET /api/v1/films/trending
  getTrendingFilms: async (days = 7, limit = 20) => {
    try {
      const response = await api.get('/api/v1/films/trending', {
        params: { days, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching trending films:', error);
      return {
        period_days: days,
        total: 0,
        films: []
      };
    }
  },

  // U main.py piše: GET /api/v1/cities/popular
  getPopularCities: async (limit = 20, min_population = 100000, country_code = null) => {
    try {
      const params = { limit, min_population };
      if (country_code) params.country_code = country_code;

      const response = await api.get('/api/v1/cities/popular', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching popular cities:', error);
      return {
        total: 0,
        cities: [],
        min_population: min_population
      };
    }
  },

  // U main.py piše: GET /api/v1/analytics/films-by-country
  getFilmsByCountry: async () => {
    try {
      const response = await api.get('/api/v1/analytics/films-by-country');
      return response.data;
    } catch (error) {
      console.error('Error fetching films by country:', error);
      return {
        total_films: 0,
        countries_analyzed: 0,
        data: []
      };
    }
  },

  // U main.py piše: GET /api/v1/analytics/cities-near-films
  getCitiesNearFilmLocations: async (radius_km = 100, limit = 20) => {
    try {
      const response = await api.get('/api/v1/analytics/cities-near-films', {
        params: { radius_km, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching cities near film locations:', error);
      return {
        radius_km: radius_km,
        locations_analyzed: 0,
        nearby_cities_found: 0,
        cities: []
      };
    }
  },

  // U main.py piše: GET /api/v1/analytics/stats
  getAnalyticsStats: async () => {
    try {
      const response = await api.get('/api/v1/analytics/stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics stats:', error);
      return {
        timestamp: new Date().toISOString(),
        counts: {
          films: 0,
          cities: 0,
          film_locations: 0,
          etl_jobs: 0
        },
        etl_stats: []
      };
    }
  }
};

// Test funkcija za endpointove
export const testAPIEndpoints = async () => {
  console.log('🔍 Testing API endpoints...');

  const endpoints = [
    { method: 'GET', url: '/api/v1/etl/status', name: 'ETL Status' },
    { method: 'GET', url: '/api/v1/etl/test', name: 'ETL Test' },
    { method: 'GET', url: '/api/v1/etl/jobs/latest', name: 'Latest Jobs' },
    { method: 'POST', url: '/api/v1/etl/run-tmdb-etl', name: 'TMDB ETL' },
    { method: 'POST', url: '/api/v1/etl/run-places-etl', name: 'Places ETL' }
  ];

  for (const endpoint of endpoints) {
    try {
      let response;
      if (endpoint.method === 'GET') {
        response = await api.get(endpoint.url);
      } else {
        response = await api.post(endpoint.url, {});
      }

      console.log(`✅ ${endpoint.name}: ${response.status}`);
    } catch (error) {
      console.log(`❌ ${endpoint.name}: ${error.response?.status || error.message}`);
    }
  }
};

export default {
  etl: etlAPI,
  analytics: analyticsAPI,
  testEndpoints: testAPIEndpoints
};