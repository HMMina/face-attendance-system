import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  AppBar,
  Toolbar,
  Chip,
  IconButton,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Home as HomeIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Assessment as ReportsIcon,
  DevicesOther as DeviceIcon
} from '@mui/icons-material';
import { getDevices, addDevice, updateDevice, deleteDevice } from '../services/api';

export default function Devices() {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [open, setOpen] = useState(false);
  const [editingDevice, setEditingDevice] = useState(null);
  const [formData, setFormData] = useState({
    device_id: '',
    name: '',
    ip_address: '',
    is_active: true
  });

  const fetchDevices = async () => {
    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      const result = await getDevices();
      
      if (result.success) {
        const devicesData = result.data || [];
        setDevices(devicesData);
      } else {
        throw new Error(result.error || 'Failed to fetch devices from database');
      }
    } catch (err) {
      console.error('❌ Error fetching devices from database:', err);
      setError(err.message || 'Không thể tải danh sách thiết bị từ database');
      setDevices([]); // Don't fallback to sample data - show empty list
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
    
    // Refresh device status every minute
    const interval = setInterval(fetchDevices, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleOpenDialog = (device = null) => {
    if (device) {
      setEditingDevice(device);
      setFormData({
        device_id: device.device_id,
        name: device.name,
        ip_address: device.ip_address || '',
        is_active: device.is_active
      });
    } else {
      setEditingDevice(null);
      setFormData({
        device_id: '',
        name: '',
        ip_address: '',
        is_active: true
      });
    }
    setOpen(true);
  };

  const handleCloseDialog = () => {
    setOpen(false);
    setEditingDevice(null);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setError('');
      setSuccess('');

      if (editingDevice) {
        // Update existing device
        const result = await updateDevice(editingDevice.id, formData);
        if (result.success) {
          setSuccess('Cập nhật thiết bị thành công!');
          await fetchDevices(); // Refresh list from database
        } else {
          throw new Error(result.error || 'Failed to update device');
        }
      } else {
        // Add new device
        const result = await addDevice(formData);
        if (result.success) {
          setSuccess('Thêm thiết bị thành công!');
          await fetchDevices(); // Refresh list from database
        } else {
          throw new Error(result.error || 'Failed to add device');
        }
      }
      
      handleCloseDialog();
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
      
    } catch (err) {
      console.error('Error saving device:', err);
      setError(err.message || 'Có lỗi khi lưu thiết bị');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (deviceId) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa thiết bị này?')) {
      try {
        setError('');
        setSuccess('');
        
        const result = await deleteDevice(deviceId);
        if (result.success) {
          setSuccess('Xóa thiết bị thành công!');
          await fetchDevices(); // Refresh list from database
          
          // Clear success message after 3 seconds
          setTimeout(() => setSuccess(''), 3000);
        } else {
          throw new Error(result.error || 'Failed to delete device');
        }
      } catch (err) {
        console.error('Error deleting device:', err);
        setError(err.message || 'Có lỗi khi xóa thiết bị');
      }
    }
  };

  return (
    <Box>
      {/* Navigation Bar */}
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Quản lý thiết bị
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
        {/* Error/Success Messages */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {success}
          </Alert>
        )}
        
        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Statistics */}
        {!loading && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <DeviceIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Tổng thiết bị
                    </Typography>
                    <Typography variant="h6">
                      {devices.length}
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
                  <DeviceIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Trực tuyến
                    </Typography>
                    <Typography variant="h6">
                      {devices.filter(d => d.network_status === 'online').length}
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
                  <DeviceIcon color="error" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Ngoại tuyến
                    </Typography>
                    <Typography variant="h6">
                      {devices.filter(d => d.network_status === 'offline').length}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        )}

        {/* Device Table */}
        {!loading && (
        <Paper>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              Danh sách thiết bị
            </Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog()}
            >
              Thêm thiết bị
            </Button>
          </Box>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>STT</TableCell>
                  <TableCell>Mã thiết bị</TableCell>
                  <TableCell>Tên thiết bị</TableCell>
                  <TableCell>Địa chỉ IP</TableCell>
                  <TableCell>Trạng thái</TableCell>
                  <TableCell>Lần cuối kết nối</TableCell>
                  <TableCell>Hành động</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {devices.map((device, index) => (
                  <TableRow key={device.id}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{device.device_id}</TableCell>
                    <TableCell>{device.name}</TableCell>
                    <TableCell>{device.ip_address || 'Chưa cấu hình'}</TableCell>
                    <TableCell>
                      <Chip
                        label={device.is_active ? 'Hoạt động' : 'Không hoạt động'}
                        color={device.is_active ? 'success' : 'error'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {device.last_seen ? new Date(device.last_seen).toLocaleString('vi-VN') : 'Chưa kết nối'}
                    </TableCell>
                    <TableCell>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(device)}
                        color="primary"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDelete(device.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
        )}

        {/* Add/Edit Dialog */}
        <Dialog open={open} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingDevice ? 'Sửa thiết bị' : 'Thêm thiết bị mới'}
          </DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Mã thiết bị"
              fullWidth
              variant="outlined"
              value={formData.device_id}
              onChange={(e) => setFormData({...formData, device_id: e.target.value})}
              disabled={editingDevice} // Không cho edit mã thiết bị khi update
              helperText={editingDevice ? "Không thể thay đổi mã thiết bị" : "Nhập mã thiết bị duy nhất"}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Tên thiết bị"
              fullWidth
              variant="outlined"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Địa chỉ IP"
              fullWidth
              variant="outlined"
              value={formData.ip_address}
              onChange={(e) => setFormData({...formData, ip_address: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Trạng thái hoạt động"
              fullWidth
              variant="outlined"
              select
              value={formData.is_active}
              onChange={(e) => setFormData({...formData, is_active: e.target.value === 'true'})}
              SelectProps={{
                native: true,
              }}
            >
              <option value={true}>Hoạt động</option>
              <option value={false}>Không hoạt động</option>
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog} disabled={saving}>Hủy</Button>
            <Button 
              onClick={handleSave} 
              variant="contained"
              disabled={saving}
            >
              {saving ? 'Đang lưu...' : (editingDevice ? 'Cập nhật' : 'Thêm')}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
