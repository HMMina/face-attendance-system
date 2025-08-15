// Trang quản lý thiết bị kiosk
import React, { useEffect, useState } from 'react';
import { getDevices, addDevice, updateDevice, deleteDevice } from '../services/api';


export default function Devices() {
  const [devices, setDevices] = useState([]);
  const [deviceId, setDeviceId] = useState('');
  const [name, setName] = useState('');
  const [networkStatus, setNetworkStatus] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editDeviceId, setEditDeviceId] = useState('');
  const [editName, setEditName] = useState('');
  const [editNetworkStatus, setEditNetworkStatus] = useState('');
  const [selected, setSelected] = useState(null);

  const fetchDevices = async () => {
    const res = await getDevices();
    setDevices(res.data);
  };

  useEffect(() => {
    fetchDevices();
  }, []);

  const handleAdd = async () => {
    await addDevice({ device_id: deviceId, name, network_status: networkStatus });
    fetchDevices();
    setDeviceId('');
    setName('');
    setNetworkStatus('');
  };

  const handleEdit = (dev) => {
    setEditingId(dev.id);
    setEditDeviceId(dev.device_id);
    setEditName(dev.name);
    setEditNetworkStatus(dev.network_status);
  };

  const handleUpdate = async () => {
    await updateDevice(editingId, { device_id: editDeviceId, name: editName, network_status: editNetworkStatus });
    setEditingId(null);
    setEditDeviceId('');
    setEditName('');
    setEditNetworkStatus('');
    fetchDevices();
  };

  const handleDelete = async (id) => {
    await deleteDevice(id);
    fetchDevices();
  };

  const handleSelect = (dev) => {
    setSelected(dev);
  };

  return (
    <div style={{ padding: 32 }}>
      <h2>Quản lý thiết bị kiosk</h2>
      <div>
        <input placeholder="Device ID" value={deviceId} onChange={e => setDeviceId(e.target.value)} />
        <input placeholder="Tên thiết bị" value={name} onChange={e => setName(e.target.value)} />
        <input placeholder="Trạng thái mạng" value={networkStatus} onChange={e => setNetworkStatus(e.target.value)} />
        <button onClick={handleAdd}>Thêm</button>
      </div>
      <ul>
        {devices.map(dev => (
          <li key={dev.id}>
            <span style={{ cursor: 'pointer', color: 'blue' }} onClick={() => handleSelect(dev)}>
              {dev.device_id} - {dev.name} - {dev.network_status}
            </span>
            <button onClick={() => handleEdit(dev)} style={{ marginLeft: 8 }}>Sửa</button>
            <button onClick={() => handleDelete(dev.id)} style={{ marginLeft: 8 }}>Xóa</button>
          </li>
        ))}
      </ul>
      {editingId && (
        <div style={{ marginTop: 16 }}>
          <h4>Sửa thiết bị</h4>
          <input value={editDeviceId} onChange={e => setEditDeviceId(e.target.value)} />
          <input value={editName} onChange={e => setEditName(e.target.value)} />
          <input value={editNetworkStatus} onChange={e => setEditNetworkStatus(e.target.value)} />
          <button onClick={handleUpdate}>Lưu</button>
          <button onClick={() => setEditingId(null)} style={{ marginLeft: 8 }}>Hủy</button>
        </div>
      )}
      {selected && (
        <div style={{ marginTop: 16, border: '1px solid #ccc', padding: 16 }}>
          <h4>Chi tiết thiết bị</h4>
          <div>ID: {selected.id}</div>
          <div>Device ID: {selected.device_id}</div>
          <div>Tên: {selected.name}</div>
          <div>Trạng thái mạng: {selected.network_status}</div>
          <button onClick={() => setSelected(null)} style={{ marginTop: 8 }}>Đóng</button>
        </div>
      )}
    </div>
  );
}
