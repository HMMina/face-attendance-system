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
  CardContent
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
import { Link } from 'react-router-dom';
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
    location: '',
    ip_address: '',
    description: ''
  });

  const fetchDevices = async () => {
    try {
      setLoading(true);
      setError('');
      const result = await getDevices();
      
      if (result.success) {
        setDevices(result.data || []);
      } else {
        throw new Error(result.error || 'Failed to fetch devices');
      }
    } catch (err) {
      console.error('Error fetching devices:', err);
      setError(err.message || 'Không thể tải danh sách thiết bị');
      
      // Fallback to sample data
      setDevices([
        { id: 1, name: 'KIOSK001', device_id: 'KIOSK001', location: 'Tầng 1 - Lễ tân', ip_address: '192.168.1.101', is_active: true, last_ping: new Date().toISOString() },
        { id: 2, name: 'KIOSK002', device_id: 'KIOSK002', location: 'Tầng 2 - Phòng IT', ip_address: '192.168.1.102', is_active: true, last_ping: new Date().toISOString() },
        { id: 3, name: 'KIOSK003', device_id: 'KIOSK003', location: 'Tầng 3 - Phòng HR', ip_address: '192.168.1.103', is_active: false, last_ping: new Date(Date.now() - 300000).toISOString() },
        { id: 4, name: 'KIOSK004', device_id: 'KIOSK004', location: 'Tầng 4 - Phòng Marketing', ip_address: '192.168.1.104', is_active: true, last_ping: new Date().toISOString() }
      ]);
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
  const generateSampleDevices = () => {
    return [
      {
        id: 1,
        device_id: 'KIOSK001',
        name: 'Kiosk cổng chính',
        location: 'Tầng 1 - Cổng chính',
        network_status: 'online',
        last_seen: '2025-08-16 08:30:00'
      },
      {
        id: 2,
        device_id: 'KIOSK002',
        name: 'Kiosk văn phòng',
        location: 'Tầng 2 - Văn phòng',
        network_status: 'online',
        last_seen: '2025-08-16 08:25:00'
      },
      {
        id: 3,
        device_id: 'KIOSK003',
        name: 'Kiosk canteen',
        location: 'Tầng 1 - Căng tin',
        network_status: 'offline',
        last_seen: '2025-08-16 07:45:00'
      }
    ];
  };

  useEffect(() => {
    // Load sample devices
    setDevices(generateSampleDevices());
  }, []);

  const handleOpenDialog = (device = null) => {
    if (device) {
      setEditingDevice(device);
      setFormData({
        device_id: device.device_id,
        name: device.name,
        location: device.location,
        network_status: device.network_status
      });
    } else {
      setEditingDevice(null);
      setFormData({
        device_id: '',
        name: '',
        location: '',
        network_status: 'online'
      });
    }
    setOpen(true);
  };

  const handleCloseDialog = () => {
    setOpen(false);
    setEditingDevice(null);
  };

  const handleSave = () => {
    if (editingDevice) {
      // Update existing device
      setDevices(devices.map(d => 
        d.id === editingDevice.id 
          ? { ...d, ...formData, last_seen: new Date().toISOString().replace('T', ' ').substr(0, 19) }
          : d
      ));
    } else {
      // Add new device
      const newDevice = {
        id: Math.max(...devices.map(d => d.id), 0) + 1,
        ...formData,
        last_seen: new Date().toISOString().replace('T', ' ').substr(0, 19)
      };
      setDevices([...devices, newDevice]);
    }
    handleCloseDialog();
  };

  const handleDelete = (deviceId) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa thiết bị này?')) {
      setDevices(devices.filter(d => d.id !== deviceId));
    }
  };

  const getStatusColor = (status) => {
    return status === 'online' ? 'success' : 'error';
  };

  const getStatusText = (status) => {
    return status === 'online' ? 'Trực tuyến' : 'Ngoại tuyến';
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
        {/* Statistics */}
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

        {/* Device Table */}
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
                  <TableCell>Vị trí</TableCell>
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
                    <TableCell>{device.location}</TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(device.network_status)}
                        color={getStatusColor(device.network_status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{device.last_seen}</TableCell>
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
              label="Vị trí"
              fullWidth
              variant="outlined"
              value={formData.location}
              onChange={(e) => setFormData({...formData, location: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField
              margin="dense"
              label="Trạng thái mạng"
              fullWidth
              variant="outlined"
              select
              value={formData.network_status}
              onChange={(e) => setFormData({...formData, network_status: e.target.value})}
              SelectProps={{
                native: true,
              }}
            >
              <option value="online">Trực tuyến</option>
              <option value="offline">Ngoại tuyến</option>
            </TextField>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Hủy</Button>
            <Button onClick={handleSave} variant="contained">
              {editingDevice ? 'Cập nhật' : 'Thêm'}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
