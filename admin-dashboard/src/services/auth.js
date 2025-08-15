// Auth service quản lý đăng nhập, token
import { login, setAuthToken } from './api';

export const authenticate = async (deviceId, password) => {
  const res = await login({ device_id: deviceId, password });
  if (res.data && res.data.token) {
    setAuthToken(res.data.token);
    localStorage.setItem('admin_token', res.data.token);
    return true;
  }
  return false;
};

export const getToken = () => localStorage.getItem('admin_token');
