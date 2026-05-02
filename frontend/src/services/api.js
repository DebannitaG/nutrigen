import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const createProfile = (data) => api.post('/profile', data);
export const getRecommendations = (data) => api.post('/recommend', data);
export const sendChat = (data) => api.post('/chat', data);
export const submitFeedback = (data) => api.post('/feedback', data);
export const getFoods = () => api.get('/foods');

export default api;