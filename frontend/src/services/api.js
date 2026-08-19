import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const sendOtp = async (payload) => {
  const response = await api.post('/api/auth/send-otp', payload);
  return response.data;
};

export const verifyOtp = async (payload) => {
  const response = await api.post('/api/auth/verify-otp', payload);
  return response.data;
};

export const registerUser = async (user) => {
  const response = await api.post('/api/auth/register', user);
  return response.data;
};

export const loginUser = async (user) => {
  const response = await api.post('/api/auth/login', user);
  return response.data;
};

export const googleAuth = async (user) => {
  const response = await api.post('/api/auth/google', user);
  return response.data;
};

export const getColleges = async (params = {}) => {
  const response = await api.get('/api/colleges', { params });
  return response.data;
};

export const searchCutoffs = async (payload) => {
  const response = await api.post('/api/cutoffs/search', payload);
  return response.data;
};

export const getCollegeById = async (id) => {
  const response = await api.get(`/api/colleges/${id}`);
  return response.data;
};

export const getProfile = async () => {
  const response = await api.get('/api/profile');
  return response.data;
};

export const updateProfile = async (payload) => {
  const response = await api.put('/api/profile', payload);
  return response.data;
};

export const getAdminColleges = async () => {
  const response = await api.get('/api/admin/colleges', {
    headers: { Authorization: `Bearer ${localStorage.getItem('auth_token')}` },
  });
  return response.data;
};

export const uploadCollegeImage = async (collegeId, file) => {
  const formData = new FormData();
  formData.append('image', file);
  const response = await api.post(`/api/admin/colleges/${collegeId}/image`, formData, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};
