// Trang đăng nhập admin
import React, { useState } from 'react';
import { authenticate } from '../services/auth';

export default function Login({ onLogin }) {
  const [deviceId, setDeviceId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    const success = await authenticate(deviceId, password);
    if (success) {
      onLogin();
    } else {
      setError('Đăng nhập thất bại');
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', padding: 32 }}>
      <h2>Đăng nhập Admin</h2>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Device ID"
          value={deviceId}
          onChange={e => setDeviceId(e.target.value)}
          style={{ width: '100%', marginBottom: 8 }}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          style={{ width: '100%', marginBottom: 8 }}
        />
        <button type="submit" style={{ width: '100%' }}>Đăng nhập</button>
      </form>
      {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
    </div>
  );
}
