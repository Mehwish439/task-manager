import axios from 'axios';

// Set your backend API base URL
const API_URL = 'http://127.0.0.1:8000/api/';

// Register a new user
export const registerUser = (data) => axios.post(`${API_URL}register/`, data);

// Log in user and get token
export const loginUser = (data) => axios.post(`${API_URL}login/`, data);

// Create a new task (requires JWT token)
export const createTask = (data, token) =>
  axios.post(`${API_URL}create-task/`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

// Get tasks assigned to the current user (requires JWT token)
export const getAssignedTasks = (token) =>
  axios.get(`${API_URL}assigned-tasks/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

// Update a specific task (requires JWT token)
export const updateTask = (id, data, token) =>
  axios.put(`${API_URL}update-task/${id}/`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

