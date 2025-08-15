// Trang quản lý nhân viên
import React, { useEffect, useState } from 'react';
import { getEmployees, addEmployee, updateEmployee, deleteEmployee } from '../services/api';


export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [name, setName] = useState('');
  const [department, setDepartment] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');
  const [editDepartment, setEditDepartment] = useState('');
  const [selected, setSelected] = useState(null);

  const fetchEmployees = async () => {
    const res = await getEmployees();
    setEmployees(res.data);
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleAdd = async () => {
    await addEmployee({ name, department });
    fetchEmployees();
    setName('');
    setDepartment('');
  };

  const handleEdit = (emp) => {
    setEditingId(emp.id);
    setEditName(emp.name);
    setEditDepartment(emp.department);
  };

  const handleUpdate = async () => {
    await updateEmployee(editingId, { name: editName, department: editDepartment });
    setEditingId(null);
    setEditName('');
    setEditDepartment('');
    fetchEmployees();
  };

  const handleDelete = async (id) => {
    await deleteEmployee(id);
    fetchEmployees();
  };

  const handleSelect = (emp) => {
    setSelected(emp);
  };

  return (
    <div style={{ padding: 32 }}>
      <h2>Quản lý nhân viên</h2>
      <div>
        <input placeholder="Tên nhân viên" value={name} onChange={e => setName(e.target.value)} />
        <input placeholder="Phòng ban" value={department} onChange={e => setDepartment(e.target.value)} />
        <button onClick={handleAdd}>Thêm</button>
      </div>
      <ul>
        {employees.map(emp => (
          <li key={emp.id}>
            <span style={{ cursor: 'pointer', color: 'blue' }} onClick={() => handleSelect(emp)}>
              {emp.name} - {emp.department}
            </span>
            <button onClick={() => handleEdit(emp)} style={{ marginLeft: 8 }}>Sửa</button>
            <button onClick={() => handleDelete(emp.id)} style={{ marginLeft: 8 }}>Xóa</button>
          </li>
        ))}
      </ul>
      {editingId && (
        <div style={{ marginTop: 16 }}>
          <h4>Sửa nhân viên</h4>
          <input value={editName} onChange={e => setEditName(e.target.value)} />
          <input value={editDepartment} onChange={e => setEditDepartment(e.target.value)} />
          <button onClick={handleUpdate}>Lưu</button>
          <button onClick={() => setEditingId(null)} style={{ marginLeft: 8 }}>Hủy</button>
        </div>
      )}
      {selected && (
        <div style={{ marginTop: 16, border: '1px solid #ccc', padding: 16 }}>
          <h4>Chi tiết nhân viên</h4>
          <div>ID: {selected.id}</div>
          <div>Tên: {selected.name}</div>
          <div>Phòng ban: {selected.department}</div>
          <button onClick={() => setSelected(null)} style={{ marginTop: 8 }}>Đóng</button>
        </div>
      )}
    </div>
  );
}
