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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  IconButton
} from '@mui/material';
import {
  Home as HomeIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Assessment as ReportsIcon,
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

export default function AdvancedDashboard() {
  const [stats, setStats] = useState({
    totalEmployees: 45,
    presentToday: 38,
    lateToday: 5,
    absentToday: 2,
    onlineDevices: 3,
    totalDevices: 4,
    weeklyAttendance: 87.5,
    monthlyAttendance: 91.2
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);

  // Generate sample data
  const generateSampleActivity = () => {
    const activities = [
      { id: 1, employee: 'Nguyễn Văn A', action: 'Check in', time: '08:15', status: 'success' },
      { id: 2, employee: 'Trần Thị B', action: 'Check out', time: '17:30', status: 'success' },
      { id: 3, employee: 'Lê Văn C', action: 'Check in', time: '08:45', status: 'warning' },
      { id: 4, employee: 'Phạm Thị D', action: 'Check in', time: '07:55', status: 'success' },
      { id: 5, employee: 'Hoàng Văn E', action: 'Check out', time: '17:15', status: 'success' }
    ];
    return activities;
  };

  const generateSampleAlerts = () => {
    const alerts = [
      { id: 1, type: 'warning', message: 'KIOSK003 ngoại tuyến từ 07:45', time: '2 giờ trước' },
      { id: 2, type: 'info', message: '5 nhân viên đến muộn hôm nay', time: '1 giờ trước' },
      { id: 3, type: 'success', message: 'Sao lưu dữ liệu hoàn tất', time: '30 phút trước' },
      { id: 4, type: 'error', message: 'Lỗi kết nối database', time: '15 phút trước' }
    ];
    return alerts;
  };

  useEffect(() => {
    setRecentActivity(generateSampleActivity());
    setAlerts(generateSampleAlerts());
  }, []);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => {
      setRecentActivity(generateSampleActivity());
      setAlerts(generateSampleAlerts());
      setLoading(false);
    }, 1000);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getAlertColor = (type) => {
    switch (type) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'error';
      case 'info': return 'info';
      default: return 'default';
    }
  };

  const attendancePercentage = (stats.presentToday / stats.totalEmployees) * 100;
  const devicePercentage = (stats.onlineDevices / stats.totalDevices) * 100;

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Navigation Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <DashboardIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Dashboard Nâng cao
          </Typography>
          <IconButton color="inherit" onClick={handleRefresh}>
            <RefreshIcon />
          </IconButton>
          <Button color="inherit" component={Link} to="/employees" startIcon={<PeopleIcon />}>
            Nhân viên
          </Button>
          <Button color="inherit" component={Link} to="/attendance" startIcon={<HistoryIcon />}>
            Chấm công
          </Button>
          <Button color="inherit" component={Link} to="/devices">
            Thiết bị
          </Button>
          <Button color="inherit" component={Link} to="/reports" startIcon={<ReportsIcon />}>
            Báo cáo
          </Button>
          <Button color="inherit" component={Link} to="/settings" startIcon={<SettingsIcon />}>
            Cài đặt
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Quick Stats */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PeopleIcon color="primary" sx={{ mr: 1 }} />
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
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Có mặt hôm nay
                    </Typography>
                    <Typography variant="h4">
                      {stats.presentToday}
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      {attendancePercentage.toFixed(1)}%
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
                  <ScheduleIcon color="warning" sx={{ mr: 1 }} />
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
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <WarningIcon color="error" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Vắng hôm nay
                    </Typography>
                    <Typography variant="h4">
                      {stats.absentToday}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Progress Indicators */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Tỷ lệ chấm công hôm nay
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Có mặt</Typography>
                    <Typography variant="body2">{attendancePercentage.toFixed(1)}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={attendancePercentage} 
                    sx={{ height: 10, borderRadius: 1 }}
                    color="success"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Trạng thái thiết bị
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Trực tuyến</Typography>
                    <Typography variant="body2">{devicePercentage.toFixed(1)}%</Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={devicePercentage} 
                    sx={{ height: 10, borderRadius: 1 }}
                    color={devicePercentage > 80 ? "success" : "warning"}
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Recent Activity & Alerts */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={8}>
            <Paper>
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                <Typography variant="h6">
                  Hoạt động gần đây
                </Typography>
              </Box>
              {loading ? (
                <LinearProgress />
              ) : (
                <TableContainer sx={{ maxHeight: 400 }}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Nhân viên</TableCell>
                        <TableCell>Hành động</TableCell>
                        <TableCell>Thời gian</TableCell>
                        <TableCell>Trạng thái</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {recentActivity.map((activity) => (
                        <TableRow key={activity.id}>
                          <TableCell>{activity.employee}</TableCell>
                          <TableCell>{activity.action}</TableCell>
                          <TableCell>{activity.time}</TableCell>
                          <TableCell>
                            <Chip
                              label={activity.status === 'success' ? 'Thành công' : 'Muộn'}
                              color={getStatusColor(activity.status)}
                              size="small"
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </Paper>
          </Grid>

          <Grid item xs={12} md={4}>
            <Paper>
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                <Typography variant="h6">
                  Cảnh báo hệ thống
                </Typography>
              </Box>
              <Box sx={{ p: 2 }}>
                {alerts.map((alert) => (
                  <Box key={alert.id} sx={{ mb: 2, p: 2, border: 1, borderRadius: 1, borderColor: 'divider' }}>
                    <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 1 }}>
                      <Chip
                        label={alert.type}
                        color={getAlertColor(alert.type)}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                      <Typography variant="caption" color="textSecondary">
                        {alert.time}
                      </Typography>
                    </Box>
                    <Typography variant="body2">
                      {alert.message}
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          </Grid>
        </Grid>

        {/* Quick Actions */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Hành động nhanh
          </Typography>
          <Grid container spacing={2}>
            <Grid item>
              <Button
                variant="contained"
                component={Link}
                to="/employees"
                startIcon={<PeopleIcon />}
              >
                Quản lý nhân viên
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                component={Link}
                to="/attendance"
                startIcon={<HistoryIcon />}
              >
                Xem chấm công
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                component={Link}
                to="/reports"
                startIcon={<TrendingUpIcon />}
              >
                Tạo báo cáo
              </Button>
            </Grid>
            <Grid item>
              <Button
                variant="outlined"
                component={Link}
                to="/settings"
                startIcon={<SettingsIcon />}
              >
                Cài đặt
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
}
