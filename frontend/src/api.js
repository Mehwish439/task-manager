import axios from 'axios';

//  Use Vite environment variable for API URL
// In your .env file: VITE_API_URL=http://localhost:8000/api/ (dev)
// Production: VITE_API_URL=https://mehwishshakoor.pythonanywhere.com/api/
const API_URL = import.meta.env.VITE_API_URL;

// Create Axios instance
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

//  Automatically attach JWT token to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ===================== AUTH =====================

// Register new user
export const registerUser = (data) => api.post('register/', data);

// Login user (JWT)
export const loginUser = (data) => api.post('login/', data);

// ===================== TASKS =====================

// Create a new task
export const createTask = (data) => api.post('create-task/', data);

// Get tasks assigned to current user
export const getAssignedTasks = () => api.get('assigned-tasks/');

// Update task status/details
export const updateTask = (id, data) => api.put(`update-task/${id}/`, data);

export default api;
