import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// attach token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// AUTH
export const registerUser = (data) => api.post('register/', data);
export const loginUser = (data) => api.post('login/', data);

// TASKS
export const createTask = (data) => api.post('create-task/', data);
export const getAssignedTasks = () => api.get('assigned-tasks/');
export const updateTask = (id, data) => api.put(`update-task/${id}/`, data);

// SAAS
export const signupCompany = (data) => api.post('signup/company/', data);
export const joinViaInvite = (data) => api.post('signup/join/', data);

export const listInvites = () => api.get('invites/');
export const createInvite = (data) => api.post('invites/', data);
export const toggleInvite = (id) => api.post(`invites/${id}/toggle/`);

export const fetchAdminStats = () => api.get('admin/stats/');
export const fetchAdminCompanies = () => api.get('admin/companies/');
export const fetchAdminCompany = (id) => api.get(`admin/companies/${id}/`);
export const toggleAdminCompany = (id) => api.post(`admin/companies/${id}/toggle/`);
export const updateAdminCompanyPlan = (id, data) =>
  api.patch(`admin/companies/${id}/plan/`, data);

export default api;