// Trang dashboard tổng quan - Kết nối database thực tế
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Box,
  AppBar,
  Toolbar,
  Paper,
  LinearProgress,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Assessment as ReportsIcon,
  Devices as DevicesIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { getEmployees, getDevices, getAllAttendance } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    presentToday: 0,
    onTimeToday: 0,
    lateToday: 0,
    absentToday: 0,
    onlineDevices: 0,
    totalDevices: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch employees
      const employeesResult = await getEmployees();
      if (!employeesResult.success) {
        throw new Error(employeesResult.error || 'Failed to fetch employees');
      }

      // Fetch devices
      const devicesResult = await getDevices();
      if (!devicesResult.success) {
        throw new Error(devicesResult.error || 'Failed to fetch devices');
      }

      // Fetch attendance data
      const attendanceResult = await getAllAttendance();
      if (!attendanceResult.success) {
        throw new Error(attendanceResult.error || 'Failed to fetch attendance');
      }

      const employees = employeesResult.data || [];
      const devices = devicesResult.data || [];
      const attendance = attendanceResult.data || [];

      // Calculate today's attendance
      const today = new Date().toISOString().split('T')[0];
      const todayAttendance = attendance.filter(record => 
        record.check_in_time && record.check_in_time.startsWith(today)
      );

      const presentEmployees = new Set(todayAttendance.map(record => record.employee_id));
      const lateEmployees = todayAttendance.filter(record => {
        // Assume work starts at 8:00 AM
        const checkInTime = new Date(record.check_in_time);
        const workStartTime = new Date(checkInTime);
        workStartTime.setHours(8, 0, 0, 0);
        return checkInTime > workStartTime;
      });

      const onlineDevices = devices.filter(device => device.status === 'online' || device.is_active).length;

      setStats({
        totalEmployees: employees.length,
        presentToday: presentEmployees.size,
        onTimeToday: presentEmployees.size - lateEmployees.length,
        lateToday: lateEmployees.length,
        absentToday: employees.length - presentEmployees.size,
        onlineDevices: onlineDevices,
        totalDevices: devices.length
      });

    } catch (err) {
      console.error('Dashboard data fetch error:', err);
      setError(err.message || 'Không thể tải dữ liệu dashboard');
      
      // Fallback to sample data if API fails
      setStats({
        totalEmployees: 45,
        presentToday: 38,
        onTimeToday: 33,
        lateToday: 5,
        absentToday: 7,
        onlineDevices: 3,
        totalDevices: 4
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const attendancePercentage = (stats.presentToday / stats.totalEmployees) * 100;
  const devicePercentage = (stats.onlineDevices / stats.totalDevices) * 100;

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Navigation Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <DashboardIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Face Attendance System
          </Typography>
          <Button color="inherit" component={Link} to="/employees" startIcon={<PeopleIcon />}>
            Nhân viên
          </Button>
          <Button color="inherit" component={Link} to="/attendance" startIcon={<HistoryIcon />}>
            Chấm công
          </Button>
          <Button color="inherit" component={Link} to="/devices" startIcon={<DevicesIcon />}>
            Thiết bị
          </Button>
          <Button color="inherit" component={Link} to="/reports" startIcon={<ReportsIcon />}>
            Báo cáo
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Error Alert */}
        {error && (
          <Alert severity="warning" sx={{ mb: 3 }}>
            {error} - Hiển thị dữ liệu mẫu
          </Alert>
        )}

        {/* Header */}
        <Box display="flex" alignItems="center" mb={3}>
          <DashboardIcon sx={{ mr: 1, fontSize: 40, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Dashboard Quản lý
          </Typography>
          {loading && <CircularProgress size={24} sx={{ ml: 2 }} />}
        </Box>

        <Typography variant="h6" color="textSecondary" mb={4}>
          Hệ thống quản lý chấm công bằng nhận diện khuôn mặt - Dữ liệu thời gian thực
        </Typography>

        {/* Quick Stats */}
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <PeopleIcon color="primary" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Tổng nhân viên
                    </Typography>
                    <Typography variant="h4">
                      {stats.totalEmployees}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <CheckCircleIcon color="success" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Có mặt hôm nay
                    </Typography>
                    <Typography variant="h4">
                      {stats.presentToday}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <ScheduleIcon color="warning" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Muộn hôm nay
                    </Typography>
                    <Typography variant="h4">
                      {stats.lateToday}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center">
                  <DevicesIcon color="info" sx={{ mr: 2, fontSize: 40 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Thiết bị online
                    </Typography>
                    <Typography variant="h4">
                      {stats.onlineDevices}/{stats.totalDevices}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Progress Indicators */}
        <Grid container spacing={3} mb={4}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Tỷ lệ chấm công hôm nay
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" sx={{ minWidth: 35 }}>
                  {attendancePercentage.toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={attendancePercentage}
                  sx={{ flexGrow: 1, ml: 1, height: 10, borderRadius: 1 }}
                  color="success"
                />
              </Box>
              <Typography variant="body2" color="textSecondary">
                {stats.presentToday} / {stats.totalEmployees} nhân viên có mặt
              </Typography>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Trạng thái thiết bị
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography variant="body2" sx={{ minWidth: 35 }}>
                  {devicePercentage.toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={devicePercentage}
                  sx={{ flexGrow: 1, ml: 1, height: 10, borderRadius: 1 }}
                  color={devicePercentage > 80 ? "success" : "warning"}
                />
              </Box>
              <Typography variant="body2" color="textSecondary">
                {stats.onlineDevices} / {stats.totalDevices} thiết bị hoạt động
              </Typography>
            </Paper>
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Typography variant="h5" mb={3}>
          Truy cập nhanh
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <PeopleIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Quản lý nhân viên
                </Typography>
                <Typography variant="body2" color="textSecondary" mb={2}>
                  Thêm, sửa, xóa thông tin nhân viên và quản lý danh sách
                </Typography>
                <Button
                  variant="contained"
                  component={Link}
                  to="/employees"
                  startIcon={<PeopleIcon />}
                  fullWidth
                >
                  Xem chi tiết
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <HistoryIcon sx={{ fontSize: 60, color: 'success.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Lịch sử chấm công
                </Typography>
                <Typography variant="body2" color="textSecondary" mb={2}>
                  Xem lịch sử check-in/out và theo dõi thời gian làm việc
                </Typography>
                <Button
                  variant="contained"
                  component={Link}
                  to="/attendance"
                  startIcon={<HistoryIcon />}
                  fullWidth
                  color="success"
                >
                  Xem chi tiết
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <DevicesIcon sx={{ fontSize: 60, color: 'info.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Quản lý thiết bị
                </Typography>
                <Typography variant="body2" color="textSecondary" mb={2}>
                  Giám sát và quản lý các kiosk chấm công trong hệ thống
                </Typography>
                <Button
                  variant="contained"
                  component={Link}
                  to="/devices"
                  startIcon={<DevicesIcon />}
                  fullWidth
                  color="info"
                >
                  Xem chi tiết
                </Button>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <ReportsIcon sx={{ fontSize: 60, color: 'warning.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Báo cáo
                </Typography>
                <Typography variant="body2" color="textSecondary" mb={2}>
                  Tạo và xuất báo cáo chấm công theo thời gian và phòng ban
                </Typography>
                <Button
                  variant="contained"
                  component={Link}
                  to="/reports"
                  startIcon={<ReportsIcon />}
                  fullWidth
                  color="warning"
                >
                  Xem chi tiết
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
