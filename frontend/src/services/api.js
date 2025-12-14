import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor za dodavanje tokena
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// AUTH API FUNCTIONS
export const authAPI = {
  // Registracija
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  // Login
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);

    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }

    return response.data;
  },

  // Logout
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// FILM API FUNCTIONS
export const filmAPI = {
  // Get popular films
  getPopularFilms: async (limit = 4) => {
    try {
      const response = await api.get(`/api/v1/films/popular?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching popular films:', error);
      throw error;
    }
  },

  // Get trending films
  getTrendingFilms: async (days = 7, limit = 20) => {
    try {
      const response = await api.get(`/api/v1/films/trending?days=${days}&limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching trending films:', error);
      throw error;
    }
  },

  // Get films with locations
  getFilmsWithLocations: async (limit = 50, skip = 0, filters = {}) => {
    try {
      const params = { limit, skip, ...filters };
      const response = await api.get(`/api/v1/films/locations`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching films with locations:', error);
      throw error;
    }
  },

  // Get featured cities
  getFeaturedCities: async (limit = 4, use_api = true) => {
    try {
      const response = await api.get(`/api/v1/cities/featured?limit=${limit}&use_api=${use_api}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching featured cities:', error);
      throw error;
    }
  }
};

// REGIONAL MAP API FUNCTIONS - NOVO
export const mapAPI = {
  // Get regional popularity map data
  getRegionalPopularity: async () => {
    try {
      const response = await api.get('/api/v1/map/regional-popularity');
      return response.data;
    } catch (error) {
      console.error('Error fetching regional popularity:', error);
      throw error;
    }
  },

  // Get test minimal map data
  getTestMapData: async () => {
    try {
      const response = await api.get('/api/v1/map/test-minimal');
      return response.data;
    } catch (error) {
      console.error('Error fetching test map data:', error);
      throw error;
    }
  }
};

// Helper functions
export const fetchPopularMovies = async (limit = 4) => {
  try {
    return await filmAPI.getPopularFilms(limit);
  } catch (error) {
    console.error('Error in fetchPopularMovies:', error);

    // Return fallback data
    return {
      source: "fallback",
      count: 4,
      films: [
        {
          film_id: 1,
          title: "The Shawshank Redemption",
          overview: "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
          release_date: "1994-09-23",
          popularity: 100,
          vote_average: 8.7,
          vote_count: 24000,
          poster_url: "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
          genres: ["Drama", "Crime"]
        },
        {
          film_id: 2,
          title: "The Godfather",
          overview: "The aging patriarch of an organized crime dynasty transfers control to his reluctant son.",
          release_date: "1972-03-24",
          popularity: 95,
          vote_average: 8.7,
          vote_count: 18000,
          poster_url: "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
          genres: ["Drama", "Crime"]
        },
        {
          film_id: 3,
          title: "The Dark Knight",
          overview: "When the menace known as the Joker wreaks havoc on Gotham City, Batman must accept one of the greatest psychological tests.",
          release_date: "2008-07-18",
          popularity: 90,
          vote_average: 8.5,
          vote_count: 30000,
          poster_url: "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
          genres: ["Action", "Crime", "Drama"]
        },
        {
          film_id: 4,
          title: "Pulp Fiction",
          overview: "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
          release_date: "1994-10-14",
          popularity: 85,
          vote_average: 8.5,
          vote_count: 25000,
          poster_url: "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
          genres: ["Crime", "Drama"]
        }
      ]
    };
  }
};

// Export all API functions
export default {
  auth: authAPI,
  film: filmAPI,
  map: mapAPI,
  api,
  fetchPopularMovies
};