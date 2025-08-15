// API service kết nối backend với error handling
import axios from 'axios';

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || 'Server error';
      throw new Error(`${error.response.status}: ${message}`);
    } else if (error.request) {
      // Network error
      throw new Error('Network error - Cannot connect to server');
    } else {
      throw new Error('Request setup error');
    }
  }
);

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

// Helper function for handling API calls
const handleApiCall = async (apiCall) => {
  try {
    const response = await apiCall();
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.message || 'Unknown error' 
    };
  }
};

// Employees with error handling
export const getEmployees = () => handleApiCall(() => api.get('/employees'));
export const addEmployee = (data) => handleApiCall(() => api.post('/employees', data));
export const updateEmployee = (id, data) => handleApiCall(() => api.put(`/employees/${id}`, data));
export const deleteEmployee = (id) => handleApiCall(() => api.delete(`/employees/${id}`));

// Devices with error handling
export const getDevices = () => handleApiCall(() => api.get('/devices'));
export const addDevice = (data) => handleApiCall(() => api.post('/devices', data));
export const updateDevice = (id, data) => handleApiCall(() => api.put(`/devices/${id}`, data));
export const deleteDevice = (id) => handleApiCall(() => api.delete(`/devices/${id}`));
export const getDeviceStatus = (id) => handleApiCall(() => api.get(`/devices/${id}`));

// Attendance with error handling
export const getAttendanceHistory = (deviceId) => handleApiCall(() => api.get(`/attendance/history/${deviceId}`));
export const getEmployeeAttendance = (employeeId) => handleApiCall(() => api.get(`/attendance/employee/${employeeId}`));
export const getAllAttendance = () => handleApiCall(() => api.get('/attendance'));

// Network with error handling
export const getNetworkStatus = () => handleApiCall(() => api.get('/network/status'));
export const getNetworkLogs = () => handleApiCall(() => api.get('/network'));
export const getDeviceNetworkLogs = (deviceId) => handleApiCall(() => api.get(`/network/device/${deviceId}`));

// Auth with error handling
export const login = (data) => handleApiCall(() => api.post('/auth/login', data));
