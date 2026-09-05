import axios from 'axios';

const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
  const cleanUrl = envUrl.replace(/\/$/, '');
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return cleanUrl.replace(/localhost|127\.0\.0\.1/, window.location.hostname);
  }
  return cleanUrl;
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = config.url?.startsWith('/api/admin')
    ? localStorage.getItem('admin_token') || localStorage.getItem('auth_token')
    : localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    return Promise.reject(error);
  }
);

export const sendOtp = async (payload) => {
  const response = await api.post('/api/auth/send-otp', payload);
  return response.data;
};

export const verifyOtp = async (payload) => {
  const response = await api.post('/api/auth/verify-otp', payload);
  return response.data;
};

export const sendLoginOtp = async (payload) => (await api.post('/api/auth/login/send-otp', payload)).data;
export const verifyLoginOtp = async (payload) => (await api.post('/api/auth/login/verify-otp', payload)).data;

export const registerUser = async (user) => {
  const response = await api.post('/api/auth/register', user);
  return response.data;
};

export const loginUser = async (user) => {
  const response = await api.post('/api/auth/login', user);
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

export const predictPercentileML = async ({ exam, marks }) => {
  const response = await api.post('/api/cutoffs/predict-percentile', {
    exam,
    marks: parseFloat(marks),
  });
  return response.data;
};

export const predictCollegesLLM = async (payload) => {
  const response = await api.post('/api/cutoffs/predict-colleges-llm', payload);
  return response.data;
};

export const getCollegeById = async (id) => {
  const response = await api.get(`/api/colleges/${id}`);
  return response.data;
};

export const lookupCollegeAI = async (query) => {
  const response = await api.get('/api/colleges/ai/lookup', { params: { q: query } });
  return response.data;
};

export const compareCollegesAI = async (college1, college2) => {
  const response = await api.get('/api/colleges/compare/ai', {
    params: { c1: college1, c2: college2 },
  });
  return response.data;
};

export const sendAssistantChat = async (message, history = []) => {
  const response = await api.post('/api/assistant', { message, history });
  return response.data;
};

export const getSavedColleges = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const local = JSON.parse(localStorage.getItem('saved_colleges_local') || '[]');
    if (!token) return local;

    const response = await api.get('/api/saved');
    const serverSaved = Array.isArray(response.data) ? response.data : [];

    const map = new Map();
    serverSaved.forEach((c) => map.set(c.college_id || c.collegeId || c.id, c));
    local.forEach((c) => {
      const key = c.college_id || c.collegeId || c.id;
      if (key && !map.has(key)) map.set(key, c);
    });
    return Array.from(map.values());
  } catch (err) {
    return JSON.parse(localStorage.getItem('saved_colleges_local') || '[]');
  }
};

export const saveCollege = async (payload) => {
  const cid = payload.college_id || payload.collegeId || payload.id;
  const normalized = {
    college_id: cid,
    collegeId: cid,
    id: cid,
    name: payload.name,
    location: payload.location || 'India',
    rating: String(payload.rating || 4.5),
    image: payload.image || null,
    savedOn: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
  };

  try {
    const local = JSON.parse(localStorage.getItem('saved_colleges_local') || '[]');
    if (!local.some((c) => (c.college_id || c.collegeId || c.id) === cid)) {
      local.unshift(normalized);
      localStorage.setItem('saved_colleges_local', JSON.stringify(local));
    }
  } catch (e) {}

  try {
    const token = localStorage.getItem('auth_token');
    if (token) {
      const response = await api.post('/api/saved', normalized);
      return response.data;
    }
  } catch (err) {
    console.warn('Saved college to local store (unauthenticated or offline server)');
  }
  return normalized;
};

export const removeSavedCollege = async (id) => {
  try {
    const local = JSON.parse(localStorage.getItem('saved_colleges_local') || '[]');
    const filtered = local.filter((c) => (c.college_id || c.collegeId || c.id) !== id);
    localStorage.setItem('saved_colleges_local', JSON.stringify(filtered));
  } catch (e) {}

  try {
    const token = localStorage.getItem('auth_token');
    if (token) {
      const response = await api.delete(`/api/saved/${id}`);
      return response.data;
    }
  } catch (err) {
    console.warn('Removed college from local store');
  }
  return { status: 'success' };
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
    headers: { Authorization: `Bearer ${localStorage.getItem('admin_token') || localStorage.getItem('auth_token')}` },
  });
  return response.data;
};

export const uploadCollegeImage = async (collegeId, file) => {
  const formData = new FormData();
  formData.append('image', file);
  const response = await api.post(`/api/admin/colleges/${collegeId}/image`, formData, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('admin_token') || localStorage.getItem('auth_token')}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const adminLogin = async (credentials) => {
  const response = await api.post('/api/admin/login', credentials);
  return response.data;
};

export const getAdminDashboard = async () => (await api.get('/api/admin/dashboard')).data;
export const getSuperAdminDashboard = async () => (await api.get('/api/admin/super-admin/dashboard')).data;
export const getAdminUsers = async (params = {}) => (await api.get('/api/admin/users', { params })).data;
export const updateAdminUser = async (id, payload) => (await api.patch(`/api/admin/users/${id}`, payload)).data;
export const deleteAdminUser = async (id) => (await api.delete(`/api/admin/users/${id}`)).data;
export const createAdminCollege = async (payload) => (await api.post('/api/admin/colleges', payload)).data;
export const updateAdminCollege = async (id, payload) => (await api.put(`/api/admin/colleges/${id}`, payload)).data;
export const deleteAdminCollege = async (id) => (await api.delete(`/api/admin/colleges/${id}`)).data;
export const getAdminCutoffs = async (params = {}) => (await api.get('/api/admin/cutoffs', { params })).data;
export const createAdminCutoff = async (payload) => (await api.post('/api/admin/cutoffs', payload)).data;
export const updateAdminCutoff = async (id, payload) => (await api.put(`/api/admin/cutoffs/${id}`, payload)).data;
export const deleteAdminCutoff = async (id) => (await api.delete(`/api/admin/cutoffs/${id}`)).data;
export const getAdminEnquiries = async (params = {}) => (await api.get('/api/admin/enquiries', { params })).data;
export const updateAdminEnquiry = async (id, payload) => (await api.patch(`/api/admin/enquiries/${id}`, payload)).data;
export const deleteAdminEnquiry = async (id) => (await api.delete(`/api/admin/enquiries/${id}`)).data;
export const getAdminSubscriptions = async () => (await api.get('/api/admin/subscriptions')).data;
export const createAdminSubscription = async (payload) => (await api.post('/api/admin/subscriptions', payload)).data;
export const updateAdminSubscription = async (id, payload) => (await api.put(`/api/admin/subscriptions/${id}`, payload)).data;
export const deleteAdminSubscription = async (id) => (await api.delete(`/api/admin/subscriptions/${id}`)).data;
export const getAdminImages = async () => (await api.get('/api/admin/images')).data;
export const uploadAdminImage = async (file, section, name) => {
  const formData = new FormData();
  formData.append('image', file);
  const response = await api.post('/api/admin/images', formData, { params: { section, name }, headers: { 'Content-Type': 'multipart/form-data' } });
  return response.data;
};
export const updateAdminImage = async (id, payload) => (await api.patch(`/api/admin/images/${id}`, payload)).data;
export const replaceAdminImage = async (id, file) => {
  const formData = new FormData();
  formData.append('image', file);
  const response = await api.post(`/api/admin/images/${id}/replace`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
  return response.data;
};
export const deleteAdminImage = async (id) => (await api.delete(`/api/admin/images/${id}`)).data;
export const trainAdminDatabase = async () => (await api.post('/api/admin/train')).data;
export const submitContactForm = async (payload) => (await api.post('/api/contact', payload)).data;
