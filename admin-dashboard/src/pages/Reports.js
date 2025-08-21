// Trang báo cáo - Tối ưu cho quản lý cơ bản
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Box,
  AppBar,
  Toolbar,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert
} from '@mui/material';
import {
  Assessment as ReportsIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Devices as DevicesIcon,
  GetApp as DownloadIcon
} from '@mui/icons-material';
import { getEmployees, getAllAttendance } from '../services/api';

export default function Reports() {
  const [reportType, setReportType] = useState('thisMonth');
  const [department, setDepartment] = useState('all');
  const [reportData, setReportData] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchReportData = async () => {
    try {
      setLoading(true);
      setError('');
      
      const [employeesResult, attendanceResult] = await Promise.all([
        getEmployees(),
        getAllAttendance()
      ]);

      if (employeesResult.success && attendanceResult.success) {
        const employees = employeesResult.data || [];
        const attendance = attendanceResult.data || [];
        
        // Calculate date range based on report type
        const now = new Date();
        let startDate, endDate, totalWorkingDays;
        
        if (reportType === 'thisMonth') {
          // This month: from 1st to last day of current month
          startDate = new Date(now.getFullYear(), now.getMonth(), 1);
          endDate = new Date(now.getFullYear(), now.getMonth() + 1, 0);
          // Calculate working days (excluding weekends)
          totalWorkingDays = getWorkingDaysInRange(startDate, endDate);
        } else {
          // This week: from Monday to Friday of current week
          const dayOfWeek = now.getDay();
          const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // Handle Sunday
          startDate = new Date(now);
          startDate.setDate(now.getDate() + mondayOffset);
          endDate = new Date(startDate);
          endDate.setDate(startDate.getDate() + 4); // Friday
          totalWorkingDays = 5; // Monday to Friday
        }
        
        // Filter attendance records within date range
        const filteredAttendance = attendance.filter(record => {
          const recordDate = new Date(record.timestamp);
          return recordDate >= startDate && recordDate <= endDate;
        });
        
        // Process data to create report
        const processedData = employees.map(employee => {
          const employeeAttendance = filteredAttendance.filter(record => 
            record.employee_id === employee.employee_id
          );
          
          // Group by date to count unique days
          const uniqueDays = new Set(
            employeeAttendance.map(record => record.timestamp.split('T')[0])
          );
          const daysPresent = uniqueDays.size;
          
          // Calculate late days (days with first check-in after 8:30 AM)
          const dailyFirstCheckin = {};
          employeeAttendance.forEach(record => {
            const date = record.timestamp.split('T')[0];
            if (!dailyFirstCheckin[date] || new Date(record.timestamp) < new Date(dailyFirstCheckin[date])) {
              dailyFirstCheckin[date] = record.timestamp;
            }
          });
          
          const daysLate = Object.values(dailyFirstCheckin).filter(timestamp => {
            const checkInTime = new Date(timestamp);
            const workStartTime = new Date(checkInTime);
            workStartTime.setHours(8, 30, 0, 0); // 8:30 AM work start time
            return checkInTime > workStartTime;
          }).length;
          
          // Calculate early leave days (days with last check-out before 18:00)
          const dailyLastCheckout = {};
          employeeAttendance.forEach(record => {
            const date = record.timestamp.split('T')[0];
            if (!dailyLastCheckout[date] || new Date(record.timestamp) > new Date(dailyLastCheckout[date])) {
              dailyLastCheckout[date] = record.timestamp;
            }
          });
          
          const daysEarlyLeave = Object.values(dailyLastCheckout).filter(timestamp => {
            const checkOutTime = new Date(timestamp);
            const workEndTime = new Date(checkOutTime);
            workEndTime.setHours(18, 0, 0, 0); // 6:00 PM work end time
            return checkOutTime < workEndTime;
          }).length;
          
          const attendanceRate = totalWorkingDays > 0 ? (daysPresent / totalWorkingDays * 100) : 0;
          
          return {
            id: employee.employee_id,
            employee: employee.name,
            department: employee.department,
            daysPresent,
            daysLate,
            daysEarlyLeave, // New field for early leave
            daysAbsent: Math.max(0, totalWorkingDays - daysPresent),
            attendanceRate: Math.round(attendanceRate * 10) / 10
          };
        });

        // Extract unique departments from employees data
        const uniqueDepartments = [...new Set(employees.map(emp => emp.department))].filter(dept => dept);
        setDepartments(uniqueDepartments);

        setReportData(processedData);
      } else {
        throw new Error('Failed to fetch report data');
      }
    } catch (err) {
      console.error('❌ Error fetching report data:', err);
      setError(err.message || 'Không thể tải dữ liệu báo cáo từ database');
      setReportData([]); // Don't fallback to sample data
    } finally {
      setLoading(false);
    }
  };

  // Helper function to calculate working days (excluding weekends)
  const getWorkingDaysInRange = (startDate, endDate) => {
    let count = 0;
    const current = new Date(startDate);
    
    while (current <= endDate) {
      const dayOfWeek = current.getDay();
      if (dayOfWeek !== 0 && dayOfWeek !== 6) { // Not Sunday (0) or Saturday (6)
        count++;
      }
      current.setDate(current.getDate() + 1);
    }
    
    return count;
  };

  useEffect(() => {
    fetchReportData();
  }, [reportType]); // Re-fetch when report type changes

  const handleExportReport = (format) => {
    alert(`Đang xuất báo cáo định dạng ${format}...`);
  };

  const handleReportTypeChange = (newType) => {
    setReportType(newType);
    // Data will be re-fetched due to useEffect dependency
  };

  const handleDepartmentChange = (newDepartment) => {
    setDepartment(newDepartment);
    // No need to re-fetch, just filter existing data
  };

  const getAttendanceColor = (rate) => {
    if (rate >= 95) return 'success';
    if (rate >= 85) return 'warning';
    return 'error';
  };

  const getDepartmentColor = (department) => {
    // Generate color based on department name hash
    const colors = ['primary', 'secondary', 'success', 'warning', 'error', 'info'];
    const hash = department.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
    return colors[hash % colors.length];
  };

  const filteredData = department === 'all' 
    ? reportData 
    : reportData.filter(item => item.department === department);

  const totalEmployees = filteredData.length;
  const avgAttendanceRate = filteredData.length > 0 
    ? (filteredData.reduce((sum, item) => sum + item.attendanceRate, 0) / filteredData.length).toFixed(1)
    : 0;
  const totalLateCount = filteredData.reduce((sum, item) => sum + item.daysLate, 0);
  const totalEarlyLeaveCount = filteredData.reduce((sum, item) => sum + item.daysEarlyLeave, 0);
  const totalAbsentCount = filteredData.reduce((sum, item) => sum + item.daysAbsent, 0);

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Navigation Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <ReportsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Báo cáo chấm công
          </Typography>
          <Button color="inherit" component={Link} to="/" startIcon={<DashboardIcon />}>
            Dashboard
          </Button>
          <Button color="inherit" component={Link} to="/employees" startIcon={<PeopleIcon />}>
            Nhân viên
          </Button>
          <Button color="inherit" component={Link} to="/attendance" startIcon={<HistoryIcon />}>
            Chấm công
          </Button>
          <Button color="inherit" component={Link} to="/devices" startIcon={<DevicesIcon />}>
            Thiết bị
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Report Controls */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Tùy chọn báo cáo
          </Typography>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel>Loại báo cáo</InputLabel>
                <Select
                  value={reportType}
                  label="Loại báo cáo"
                  onChange={(e) => handleReportTypeChange(e.target.value)}
                >
                  <MenuItem value="thisMonth">Tháng này</MenuItem>
                  <MenuItem value="thisWeek">Tuần này</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel>Phòng ban</InputLabel>
                <Select
                  value={department}
                  label="Phòng ban"
                  onChange={(e) => handleDepartmentChange(e.target.value)}
                >
                  <MenuItem value="all">Tất cả</MenuItem>
                  {departments.map((dept) => (
                    <MenuItem key={dept} value={dept}>{dept}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={12} md={4}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExportReport('Excel')}
                  size="small"
                >
                  Excel
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExportReport('PDF')}
                  size="small"
                >
                  PDF
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
            <Typography>Đang tải dữ liệu báo cáo...</Typography>
          </Box>
        )}

        {/* Error State */}
        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {/* Summary Cards */}
        {!loading && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PeopleIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Tổng nhân viên
                    </Typography>
                    <Typography variant="h5">
                      {totalEmployees}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <ReportsIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Tỷ lệ chấm công TB
                    </Typography>
                    <Typography variant="h5">
                      {avgAttendanceRate}%
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Tổng số lần muộn
                </Typography>
                <Typography variant="h5" color="warning.main">
                  {totalLateCount}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Tổng số về sớm
                </Typography>
                <Typography variant="h5" color="info.main">
                  {totalEarlyLeaveCount}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        )}

        {/* Additional Summary Card for Absent */}
        {!loading && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Tổng số ngày vắng
                </Typography>
                <Typography variant="h5" color="error.main">
                  {totalAbsentCount}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        )}

        {/* Report Table */}
        {!loading && (
        <Paper>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">
              Chi tiết báo cáo chấm công - {reportType === 'thisMonth' ? 'Tháng này' : 'Tuần này'}
            </Typography>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nhân viên</TableCell>
                  <TableCell>Phòng ban</TableCell>
                  <TableCell>Ngày có mặt</TableCell>
                  <TableCell>Ngày muộn</TableCell>
                  <TableCell>Ngày về sớm</TableCell>
                  <TableCell>Ngày vắng</TableCell>
                  <TableCell>Tỷ lệ (%)</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredData.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>{row.employee}</TableCell>
                    <TableCell>
                      <Chip
                        label={row.department}
                        color={getDepartmentColor(row.department)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{row.daysPresent}</TableCell>
                    <TableCell>{row.daysLate}</TableCell>
                    <TableCell>{row.daysEarlyLeave}</TableCell>
                    <TableCell>{row.daysAbsent}</TableCell>
                    <TableCell>
                      <Chip
                        label={`${row.attendanceRate}%`}
                        color={getAttendanceColor(row.attendanceRate)}
                        size="small"
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
        )}
      </Container>
    </Box>
  );
}
