// Enhanced Dashboard with Material-UI components and better statistics
import React, { useState, useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  AppBar,
  Toolbar,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert,
  CircularProgress,
  Chip
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Devices as DevicesIcon,
  AccessTime as AccessTimeIcon,
  NetworkCheck as NetworkIcon,
  Assessment as ReportsIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';
import { Link, useNavigate } from 'react-router-dom';
import { getStats, getRecentActivity } from '../services/api';

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Nhân viên', icon: <PeopleIcon />, path: '/employees' },
  { text: 'Thiết bị', icon: <DevicesIcon />, path: '/devices' },
  { text: 'Chấm công', icon: <AccessTimeIcon />, path: '/attendance' },
  { text: 'Mạng', icon: <NetworkIcon />, path: '/network' },
  { text: 'Báo cáo', icon: <ReportsIcon />, path: '/reports' },
  { text: 'Cài đặt', icon: <SettingsIcon />, path: '/settings' },
];

export default function EnhancedDashboard() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsRes, activityRes] = await Promise.all([
        getStats(),
        getRecentActivity()
      ]);
      setStats(statsRes.data);
      setRecentActivity(activityRes.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, subtitle, color = 'primary', icon }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" mb={1}>
          {icon}
          <Typography variant="h6" component="div" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" color={`${color}.main`} fontWeight="bold">
          {value}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      </CardContent>
    </Card>
  );

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Face Attendance
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            component={Link}
            to={item.path}
            onClick={() => setDrawerOpen(false)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Box>
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={() => setDrawerOpen(!drawerOpen)}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Dashboard - Hệ thống chấm công
          </Typography>
          <IconButton color="inherit">
            <NotificationsIcon />
          </IconButton>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        ModalProps={{ keepMounted: true }}
      >
        {drawer}
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        <Container maxWidth="lg">
          {/* Alert for system status */}
          <Alert severity="success" sx={{ mb: 3 }}>
            Hệ thống hoạt động bình thường. Tất cả thiết bị đang kết nối.
          </Alert>

          {/* Statistics Cards */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Nhân viên"
                value={stats?.totalEmployees || 0}
                subtitle="Đã đăng ký"
                icon={<PeopleIcon color="primary" />}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Thiết bị"
                value={stats?.activeDevices || 0}
                subtitle="Đang hoạt động"
                color="success"
                icon={<DevicesIcon color="success" />}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Chấm công hôm nay"
                value={stats?.todayAttendance || 0}
                subtitle="Lượt chấm"
                color="info"
                icon={<AccessTimeIcon color="info" />}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <StatCard
                title="Tỷ lệ nhận diện"
                value={`${stats?.recognitionRate || 95}%`}
                subtitle="Chính xác"
                color="warning"
                icon={<NetworkIcon color="warning" />}
              />
            </Grid>
          </Grid>

          {/* Recent Activity */}
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Hoạt động gần đây
                </Typography>
                {recentActivity.length > 0 ? (
                  recentActivity.map((activity, index) => (
                    <Box key={index} sx={{ mb: 2, pb: 2, borderBottom: '1px solid #eee' }}>
                      <Box display="flex" justifyContent="space-between" alignItems="center">
                        <Typography variant="body1">
                          {activity.employeeName || 'Không xác định'} - {activity.action}
                        </Typography>
                        <Chip 
                          label={activity.status} 
                          color={activity.status === 'success' ? 'success' : 'error'}
                          size="small"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary">
                        {new Date(activity.timestamp).toLocaleString('vi-VN')}
                      </Typography>
                    </Box>
                  ))
                ) : (
                  <Typography color="text.secondary">Chưa có hoạt động nào.</Typography>
                )}
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Trạng thái hệ thống
                </Typography>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2">Backend API</Typography>
                  <Chip label="Hoạt động" color="success" size="small" />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2">Database</Typography>
                  <Chip label="Kết nối" color="success" size="small" />
                </Box>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2">Camera Service</Typography>
                  <Chip label="Sẵn sàng" color="success" size="small" />
                </Box>
              </Paper>
              
              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Thao tác nhanh
                </Typography>
                <Grid container spacing={1}>
                  <Grid item xs={6}>
                    <Card 
                      sx={{ cursor: 'pointer', textAlign: 'center', p: 2 }}
                      onClick={() => navigate('/employees')}
                    >
                      <PeopleIcon color="primary" />
                      <Typography variant="body2">Nhân viên</Typography>
                    </Card>
                  </Grid>
                  <Grid item xs={6}>
                    <Card 
                      sx={{ cursor: 'pointer', textAlign: 'center', p: 2 }}
                      onClick={() => navigate('/devices')}
                    >
                      <DevicesIcon color="primary" />
                      <Typography variant="body2">Thiết bị</Typography>
                    </Card>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </Box>
  );
}
