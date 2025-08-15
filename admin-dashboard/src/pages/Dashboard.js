// Trang dashboard tổng quan
import React from 'react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  return (
    <div style={{ padding: 32 }}>
      <h2>Face Attendance Dashboard</h2>
      <p>Quản lý nhân viên, thiết bị, lịch sử chấm công, báo cáo và giám sát mạng.</p>
      <nav style={{ marginTop: 24 }}>
        <Link to="/employees" style={{ marginRight: 16 }}>Nhân viên</Link>
        <Link to="/devices" style={{ marginRight: 16 }}>Thiết bị kiosk</Link>
        <Link to="/attendance" style={{ marginRight: 16 }}>Lịch sử chấm công</Link>
        <Link to="/network" style={{ marginRight: 16 }}>Giám sát mạng</Link>
        <Link to="/reports">Báo cáo</Link>
      </nav>
    </div>
  );
}
