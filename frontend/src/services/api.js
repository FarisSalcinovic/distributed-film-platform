// frontend/src/services/api.js
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Kreiraj axios instancu
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token interceptor
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

// ================= AUTH =================
export const authAPI = {
  register: async (userData) => (await api.post('/auth/register', userData)).data,
  login: async (credentials) => {
    const res = await api.post('/auth/login', credentials);
    if (res.data.access_token) {
      localStorage.setItem('access_token', res.data.access_token);
      localStorage.setItem('refresh_token', res.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(res.data.user));
    }
    return res.data;
  },
  logout: async () => {
    try {
      await api.post('/auth/logout');
    } finally {
      localStorage.clear();
    }
  },
  getCurrentUser: async () => (await api.get('/auth/me')).data,
};

// ================= FILMS =================
export const filmAPI = {
  // ⭐ TOP 3 FILMA PO REGIJI
  getPopularFilmsByRegion: async (region, limit = 3) => {
    const response = await api.get('/api/v1/films/popular-region', {
      params: { region, limit }
    });
    return response.data;
  }
};

// ================= MAP =================
export const mapAPI = {
  getRegionalPopularity: async () =>
    (await api.get('/api/v1/map/regional-popularity')).data
};

// VAŽNO: Ostavi i default export za backward compatibility
export default {
  api,
  auth: authAPI,
  film: filmAPI,
  map: mapAPI
};