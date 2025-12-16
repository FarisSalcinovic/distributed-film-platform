// frontend/src/services/etlApi.js
import { api } from './api'; // VAŽNO: Import named export 'api'

// ETL API Services
export const etlAPI = {
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
};

// Analytics API Services
export const analyticsAPI = {
  getFilmsWithLocations: async (limit = 50, skip = 0, filters = {}) => {
    try {
      const params = { limit, skip, ...filters };
      const response = await api.get('/api/v1/films/locations', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching films with locations:', error);
      return { total: 0, films: [], filters };
    }
  },

  getPopularFilmsByRegion: async (region, limit = 3) => {
    try {
      console.log('🔥 etlApi.js: Pozivam API za region:', region);

      const response = await api.get('/api/v1/films/popular-region', {
        params: {
          region: region,
          limit: limit
        }
      });

      console.log('✅ etlApi.js: API odgovor:', response.data);
      return response.data;

    } catch (error) {
      console.error('❌ etlApi.js: Greška pri pozivu API-ja:', error);

      if (error.response) {
        console.error('Status:', error.response.status);
        console.error('Podaci:', error.response.data);
        console.error('URL:', error.config?.url);
      } else if (error.request) {
        console.error('Nema odgovora od servera');
      }

      // Vrati prazan niz za slučaj greške
      return { films: [], region };
    }
  },

  getTrendingFilms: async (days = 7, limit = 20) => {
    try {
      const response = await api.get('/api/v1/films/trending', { params: { days, limit } });
      return response.data;
    } catch (error) {
      console.error('Error fetching trending films:', error);
      return { period_days: days, total: 0, films: [] };
    }
  },

  // ... (ostali analytics endpointi ostaju isti)
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
      if (endpoint.method === 'GET') response = await api.get(endpoint.url);
      else response = await api.post(endpoint.url, {});
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