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
  GetApp as DownloadIcon,
  TrendingUp as TrendingUpIcon
} from '@mui/icons-material';
import { getEmployees, getAllAttendance } from '../services/api';

export default function Reports() {
  const [reportType, setReportType] = useState('monthly');
  const [department, setDepartment] = useState('all');
  const [reportData, setReportData] = useState([]);
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
        
        // Process data to create report
        const processedData = employees.map(employee => {
          const employeeAttendance = attendance.filter(record => 
            record.employee_id === employee.employee_id // Fix: use employee_id string matching
          );
          
          // Group by date to count unique days
          const uniqueDays = new Set(
            employeeAttendance.map(record => record.timestamp.split('T')[0])
          );
          const daysPresent = uniqueDays.size;
          
          // Calculate late days (days with first check-in after 8:00 AM)
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
            workStartTime.setHours(8, 0, 0, 0);
            return checkInTime > workStartTime;
          }).length;
          
          const totalWorkingDays = 22; // Assume 22 working days per month
          const attendanceRate = totalWorkingDays > 0 ? (daysPresent / totalWorkingDays * 100) : 0;
          
          return {
            id: employee.id,
            employee: employee.name,
            department: employee.department,
            daysPresent,
            daysLate,
            daysAbsent: Math.max(0, totalWorkingDays - daysPresent),
            attendanceRate: Math.round(attendanceRate * 10) / 10
          };
        });

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

  useEffect(() => {
    fetchReportData();
  }, []);

  const handleExportReport = (format) => {
    alert(`Đang xuất báo cáo định dạng ${format}...`);
  };

  const getAttendanceColor = (rate) => {
    if (rate >= 95) return 'success';
    if (rate >= 85) return 'warning';
    return 'error';
  };

  const getDepartmentColor = (department) => {
    const colors = {
      'IT': 'primary',
      'HR': 'secondary',
      'Finance': 'success',
      'Marketing': 'warning'
    };
    return colors[department] || 'default';
  };

  const filteredData = department === 'all' 
    ? reportData 
    : reportData.filter(item => item.department === department);

  const totalEmployees = filteredData.length;
  const avgAttendanceRate = filteredData.length > 0 
    ? (filteredData.reduce((sum, item) => sum + item.attendanceRate, 0) / filteredData.length).toFixed(1)
    : 0;
  const totalLateCount = filteredData.reduce((sum, item) => sum + item.daysLate, 0);
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
                  onChange={(e) => setReportType(e.target.value)}
                >
                  <MenuItem value="daily">Hàng ngày</MenuItem>
                  <MenuItem value="weekly">Hàng tuần</MenuItem>
                  <MenuItem value="monthly">Hàng tháng</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel>Phòng ban</InputLabel>
                <Select
                  value={department}
                  label="Phòng ban"
                  onChange={(e) => setDepartment(e.target.value)}
                >
                  <MenuItem value="all">Tất cả</MenuItem>
                  <MenuItem value="IT">IT</MenuItem>
                  <MenuItem value="HR">HR</MenuItem>
                  <MenuItem value="Finance">Finance</MenuItem>
                  <MenuItem value="Marketing">Marketing</MenuItem>
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
                  <TrendingUpIcon color="success" sx={{ mr: 1 }} />
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
              Chi tiết báo cáo chấm công - {reportType === 'daily' ? 'Hàng ngày' : reportType === 'weekly' ? 'Hàng tuần' : 'Hàng tháng'}
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

        {/* Chart Placeholder */}
        {!loading && (
        <Paper sx={{ mt: 3, p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Biểu đồ xu hướng chấm công
          </Typography>
          <Box sx={{ 
            height: 200, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            bgcolor: 'grey.50',
            border: '2px dashed',
            borderColor: 'grey.300',
            borderRadius: 1
          }}>
            <Typography color="textSecondary" align="center">
              Biểu đồ sẽ được hiển thị ở đây<br />
              (Cần tích hợp thư viện Chart.js hoặc Recharts)
            </Typography>
          </Box>
        </Paper>
        )}
      </Container>
    </Box>
  );
}
