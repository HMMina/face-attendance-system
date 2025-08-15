// Trang lịch sử chấm công
import React, { useState } from 'react';
import { getAttendanceHistory, getEmployeeAttendance } from '../services/api';


export default function Attendance() {
  const [deviceId, setDeviceId] = useState('');
  const [employeeId, setEmployeeId] = useState('');
  const [history, setHistory] = useState([]);
  const [selected, setSelected] = useState(null);

  const handleSearchDevice = async () => {
    const res = await getAttendanceHistory(deviceId);
    setHistory(res.data);
  };

  const handleSearchEmployee = async () => {
    const res = await getEmployeeAttendance(employeeId);
    setHistory(res.data);
  };

  const handleSelect = (item) => {
    setSelected(item);
  };

  const handleExport = () => {
    // Xuất báo cáo đơn giản dạng CSV
    const csv = history.map(h => `${h.id},${h.employee_id},${h.device_id},${h.timestamp},${h.confidence}`).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'attendance_report.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ padding: 32 }}>
      <h2>Lịch sử chấm công</h2>
      <div>
        <input placeholder="Device ID" value={deviceId} onChange={e => setDeviceId(e.target.value)} />
        <button onClick={handleSearchDevice}>Tìm theo thiết bị</button>
        <input placeholder="Employee ID" value={employeeId} onChange={e => setEmployeeId(e.target.value)} style={{ marginLeft: 8 }} />
        <button onClick={handleSearchEmployee}>Tìm theo nhân viên</button>
        <button onClick={handleExport} style={{ marginLeft: 8 }}>Xuất báo cáo</button>
      </div>
      <ul>
        {history.map(item => (
          <li key={item.id}>
            <span style={{ cursor: 'pointer', color: 'blue' }} onClick={() => handleSelect(item)}>
              {item.employee_id} - {item.device_id} - {item.timestamp} - {item.confidence}
            </span>
          </li>
        ))}
      </ul>
      {selected && (
        <div style={{ marginTop: 16, border: '1px solid #ccc', padding: 16 }}>
          <h4>Chi tiết chấm công</h4>
          <div>ID: {selected.id}</div>
          <div>Employee ID: {selected.employee_id}</div>
          <div>Device ID: {selected.device_id}</div>
          <div>Thời gian: {selected.timestamp}</div>
          <div>Độ tin cậy: {selected.confidence}</div>
          <button onClick={() => setSelected(null)} style={{ marginTop: 8 }}>Đóng</button>
        </div>
      )}
    </div>
  );
}
