// Trang đăng nhập admin
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert
} from '@mui/material';
import {
  Login as LoginIcon
} from '@mui/icons-material';

export default function Login({ onLogin }) {
  const [deviceId, setDeviceId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      // Simulate authentication
      setTimeout(() => {
        if (deviceId === 'admin' && password === 'admin') {
          if (onLogin) onLogin();
          navigate('/');
        } else {
          setError('Tên đăng nhập hoặc mật khẩu không đúng');
        }
        setLoading(false);
      }, 1000);
    } catch (err) {
      setError('Đăng nhập thất bại');
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 3 }}>
          <LoginIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom>
            Admin Dashboard
          </Typography>
          <Typography variant="subtitle1" color="textSecondary">
            Đăng nhập vào hệ thống quản lý
          </Typography>
        </Box>

        <form onSubmit={handleLogin}>
          <TextField
            fullWidth
            label="Tên đăng nhập"
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
            margin="normal"
            required
            autoFocus
          />
          <TextField
            fullWidth
            label="Mật khẩu"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            margin="normal"
            required
          />
          
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
            disabled={loading}
            startIcon={<LoginIcon />}
          >
            {loading ? 'Đang đăng nhập...' : 'Đăng nhập'}
          </Button>
        </form>

        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="caption" color="textSecondary">
            Demo: admin / admin
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}
