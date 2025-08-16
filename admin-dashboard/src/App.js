// App entry point cho Admin Dashboard - 4 chức năng cốt lõi
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Employees from './pages/Employees';
import Devices from './pages/Devices';
import Attendance from './pages/Attendance';
import Reports from './pages/Reports';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/employees" element={<Employees />} />
        <Route path="/devices" element={<Devices />} />
        <Route path="/attendance" element={<Attendance />} />
        <Route path="/reports" element={<Reports />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
