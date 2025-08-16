// Trang giám sát mạng
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Box,
  AppBar,
  Toolbar,
  Button,
  Grid,
  Paper,
  CircularProgress
} from '@mui/material';
import {
  Home as HomeIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Assessment as ReportsIcon,
  NetworkCheck as NetworkIcon
} from '@mui/icons-material';

export default function Network() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    setTimeout(() => {
      setStatus({
        service_name: 'Face Attendance API',
        status: 'Active',
        ip_address: 'localhost',
        port: '8000'
      });
      setLoading(false);
    }, 1000);
  }, []);

  return (
    <Box>
      {/* Navigation Bar */}
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Giám sát mạng
          </Typography>
          <Button color="inherit" component={Link} to="/" startIcon={<HomeIcon />}>
            Trang chủ
          </Button>
          <Button color="inherit" component={Link} to="/employees" startIcon={<PeopleIcon />}>
            Nhân viên
          </Button>
          <Button color="inherit" component={Link} to="/attendance" startIcon={<HistoryIcon />}>
            Chấm công
          </Button>
          <Button color="inherit" component={Link} to="/reports" startIcon={<ReportsIcon />}>
            Báo cáo
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg">
        <Typography variant="h4" gutterBottom>
          <NetworkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Trạng thái mạng
        </Typography>

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Dịch vụ
                  </Typography>
                  <Typography variant="h4" color="success.main">
                    {status?.service_name || 'Unknown'}
                  </Typography>
                  <Typography color="textSecondary">
                    Trạng thái: {status?.status || 'Unknown'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Kết nối
                  </Typography>
                  <Typography variant="h4" color="primary.main">
                    {status?.ip_address}:{status?.port}
                  </Typography>
                  <Typography color="textSecondary">
                    Địa chỉ máy chủ
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </Container>
    </Box>
  );
}
