// frontend/src/utils/apiTester.js
import api from '../services/api';

const apiTester = {
  testAllEndpoints: async () => {
    console.log('🧪 Testing all API endpoints...');
    console.log('Base URL:', api.defaults.baseURL);

    const testCases = [
      // ETL endpoints
      { method: 'GET', url: '/api/v1/etl/status', name: 'ETL Status', requiresAuth: false },
      { method: 'GET', url: '/api/v1/etl/test', name: 'ETL Test', requiresAuth: false },
      { method: 'GET', url: '/api/v1/etl/jobs/latest', name: 'Latest Jobs', requiresAuth: false },
      { method: 'GET', url: '/api/v1/etl/collections/stats', name: 'Collections Stats', requiresAuth: false },

      // Film Locations endpoints
      { method: 'GET', url: '/api/v1/film-locations/films/locations', name: 'Films with Locations', requiresAuth: false, params: { limit: 5 } },
      { method: 'GET', url: '/api/v1/film-locations/films/trending', name: 'Trending Films', requiresAuth: false, params: { limit: 5 } },
      { method: 'GET', url: '/api/v1/film-locations/cities/popular', name: 'Popular Cities', requiresAuth: false, params: { limit: 5 } },

      // Analytics endpoints
      { method: 'GET', url: '/api/v1/analytics/film-location-correlations', name: 'Film Location Correlations', requiresAuth: true },
      { method: 'GET', url: '/api/v1/film-locations/analytics/stats', name: 'Analytics Stats', requiresAuth: false },
    ];

    const results = [];

    for (const test of testCases) {
      try {
        const config = {};
        if (test.params) {
          config.params = test.params;
        }

        let response;
        if (test.method === 'GET') {
          response = await api.get(test.url, config);
        } else if (test.method === 'POST') {
          response = await api.post(test.url, test.data || {}, config);
        }

        results.push({
          name: test.name,
          url: test.url,
          status: response.status,
          success: true,
          data: response.data
        });

        console.log(`✅ ${test.name}: ${response.status}`);

      } catch (error) {
        results.push({
          name: test.name,
          url: test.url,
          status: error.response?.status || 'No response',
          success: false,
          error: error.message,
          fullError: error
        });

        console.log(`❌ ${test.name}: ${error.response?.status || error.message}`);

        if (error.response?.status === 404) {
          console.log(`   ↳ Endpoint not found: ${test.url}`);
        }
      }
    }

    console.log('\n📊 Test Summary:');
    console.log(`✅ Successful: ${results.filter(r => r.success).length}`);
    console.log(`❌ Failed: ${results.filter(r => !r.success).length}`);

    // Prikaži samo neuspjele testove
    const failedTests = results.filter(r => !r.success);
    if (failedTests.length > 0) {
      console.log('\n🔍 Failed endpoints:');
      failedTests.forEach(test => {
        console.log(`   • ${test.name}: ${test.url} (${test.status})`);
      });
    }

    return results;
  },

  testSpecificEndpoint: async (method, url, data = null) => {
    console.log(`🧪 Testing: ${method} ${url}`);

    try {
      let response;
      if (method === 'GET') {
        response = await api.get(url);
      } else if (method === 'POST') {
        response = await api.post(url, data || {});
      } else if (method === 'PUT') {
        response = await api.put(url, data || {});
      } else if (method === 'DELETE') {
        response = await api.delete(url);
      }

      console.log(`✅ Success: ${response.status}`);
      console.log('Response:', response.data);
      return { success: true, data: response.data };

    } catch (error) {
      console.log(`❌ Error: ${error.response?.status || error.message}`);
      console.log('Error details:', error.response?.data || error.message);
      return { success: false, error: error };
    }
  }
};

export default apiTester;