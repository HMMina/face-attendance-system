// Trang giám sát mạng
import React, { useEffect, useState } from 'react';
import { getNetworkStatus } from '../services/api';

export default function Network() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    getNetworkStatus().then(res => setStatus(res.data));
  }, []);

  return (
    <div style={{ padding: 32 }}>
      <h2>Giám sát mạng</h2>
      {status ? (
        <div>
          <p>Server: {status.service_name} ({status.status})</p>
          <p>IP: {status.ip_address || 'N/A'}</p>
          <p>Port: {status.port}</p>
        </div>
      ) : <p>Đang tải...</p>}
    </div>
  );
}
