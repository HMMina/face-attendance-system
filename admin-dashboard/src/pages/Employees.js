// Trang quản lý nhân viên - Kết nối database thực tế
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Chip,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import {
  People as PeopleIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Dashboard as DashboardIcon,
  History as HistoryIcon,
  Assessment as ReportsIcon,
  Devices as DevicesIcon,
  Person as PersonIcon,
  Work as WorkIcon
} from '@mui/icons-material';
import { getEmployees, addEmployee, updateEmployee, deleteEmployee } from '../services/api';

export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    employee_id: '',
    department: '',
    position: '',
    phone: ''
  });

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      setError('');
      const result = await getEmployees();
      
      if (result.success) {
        setEmployees(result.data || []);
      } else {
        throw new Error(result.error || 'Failed to fetch employees');
      }
    } catch (err) {
      console.error('Error fetching employees:', err);
      setError(err.message || 'Không thể tải danh sách nhân viên');
      
      // Fallback to sample data
      setEmployees([
        { id: 1, name: 'Nguyễn Văn A', email: 'nva@company.com', employee_id: 'EMP001', department: 'IT', position: 'Developer', phone: '0901234567', is_active: true },
        { id: 2, name: 'Trần Thị B', email: 'ttb@company.com', employee_id: 'EMP002', department: 'HR', position: 'HR Manager', phone: '0907654321', is_active: true },
        { id: 3, name: 'Lê Văn C', email: 'lvc@company.com', employee_id: 'EMP003', department: 'Finance', position: 'Accountant', phone: '0909876543', is_active: true },
        { id: 4, name: 'Phạm Thị D', email: 'ptd@company.com', employee_id: 'EMP004', department: 'Marketing', position: 'Marketing Specialist', phone: '0912345678', is_active: false },
        { id: 5, name: 'Hoàng Văn E', email: 'hve@company.com', employee_id: 'EMP005', department: 'IT', position: 'System Admin', phone: '0923456789', is_active: true }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, []);

  const handleOpenDialog = (employee = null) => {
    if (employee) {
      setEditingEmployee(employee);
      setFormData({
        name: employee.name,
        email: employee.email,
        employee_id: employee.employee_id,
        department: employee.department,
        position: employee.position,
        phone: employee.phone
      });
    } else {
      setEditingEmployee(null);
      setFormData({
        name: '',
        email: '',
        employee_id: '',
        department: '',
        position: '',
        phone: ''
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingEmployee(null);
    setFormData({
      name: '',
      email: '',
      employee_id: '',
      department: '',
      position: '',
      phone: ''
    });
  };

  const handleSaveEmployee = async () => {
    try {
      setSaving(true);
      setError('');
      
      let result;
      if (editingEmployee) {
        // Update existing employee
        result = await updateEmployee(editingEmployee.id, formData);
      } else {
        // Add new employee
        result = await addEmployee(formData);
      }
      
      if (result.success) {
        setSuccess(editingEmployee ? 'Cập nhật thành công!' : 'Thêm nhân viên thành công!');
        handleCloseDialog();
        fetchEmployees(); // Refresh list
      } else {
        throw new Error(result.error || 'Operation failed');
      }
    } catch (err) {
      console.error('Save employee error:', err);
      setError(err.message || 'Không thể lưu thông tin nhân viên');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteEmployee = async (id) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa nhân viên này?')) {
      try {
        setError('');
        const result = await deleteEmployee(id);
        
        if (result.success) {
          setSuccess('Xóa nhân viên thành công!');
          fetchEmployees(); // Refresh list
        } else {
          throw new Error(result.error || 'Delete failed');
        }
      } catch (err) {
        console.error('Delete employee error:', err);
        setError(err.message || 'Không thể xóa nhân viên');
      }
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const getStatusColor = (status) => {
    return status ? 'success' : 'default';
  };

  const getStatusText = (status) => {
    return status ? 'Hoạt động' : 'Không hoạt động';
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

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Navigation Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <PeopleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Quản lý nhân viên
          </Typography>
          <Button color="inherit" component={Link} to="/" startIcon={<DashboardIcon />}>
            Dashboard
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
        {/* Error/Success Messages */}
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={() => setError('')}
        >
          <Alert severity="error" onClose={() => setError('')}>
            {error}
          </Alert>
        </Snackbar>

        <Snackbar
          open={!!success}
          autoHideDuration={4000}
          onClose={() => setSuccess('')}
        >
          <Alert severity="success" onClose={() => setSuccess('')}>
            {success}
          </Alert>
        </Snackbar>

        {/* Loading indicator */}
        {loading && (
          <Box display="flex" justifyContent="center" mb={3}>
            <CircularProgress />
          </Box>
        )}
        {/* Summary Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <PersonIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Tổng nhân viên
                    </Typography>
                    <Typography variant="h5">
                      {employees.length}
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
                  <WorkIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Đang hoạt động
                    </Typography>
                    <Typography variant="h5">
                      {employees.filter(emp => emp.is_active).length}
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
                  Phòng ban IT
                </Typography>
                <Typography variant="h5">
                  {employees.filter(emp => emp.department === 'IT').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Phòng ban khác
                </Typography>
                <Typography variant="h5">
                  {employees.filter(emp => emp.department !== 'IT').length}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Add Employee Button */}
        <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h5" component="h1">
            Danh sách nhân viên
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
            size="large"
          >
            Thêm nhân viên
          </Button>
        </Box>

        {/* Employees Table */}
        <Paper>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Mã NV</TableCell>
                  <TableCell>Họ tên</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Phòng ban</TableCell>
                  <TableCell>Chức vụ</TableCell>
                  <TableCell>Điện thoại</TableCell>
                  <TableCell>Trạng thái</TableCell>
                  <TableCell>Thao tác</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {employees.map((employee) => (
                  <TableRow key={employee.id}>
                    <TableCell>{employee.employee_id}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <PersonIcon sx={{ mr: 1, color: 'text.secondary' }} />
                        {employee.name}
                      </Box>
                    </TableCell>
                    <TableCell>{employee.email}</TableCell>
                    <TableCell>
                      <Chip
                        label={employee.department}
                        color={getDepartmentColor(employee.department)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{employee.position}</TableCell>
                    <TableCell>{employee.phone}</TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(employee.is_active)}
                        color={getStatusColor(employee.is_active)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <IconButton
                        color="primary"
                        onClick={() => handleOpenDialog(employee)}
                        size="small"
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton
                        color="error"
                        onClick={() => handleDeleteEmployee(employee.id)}
                        size="small"
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

        {/* Add/Edit Employee Dialog */}
        <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>
            {editingEmployee ? 'Sửa thông tin nhân viên' : 'Thêm nhân viên mới'}
          </DialogTitle>
          <DialogContent>
            <Grid container spacing={2} sx={{ mt: 1 }}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Họ tên"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Mã nhân viên"
                  name="employee_id"
                  value={formData.employee_id}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Phòng ban"
                  name="department"
                  value={formData.department}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Chức vụ"
                  name="position"
                  value={formData.position}
                  onChange={handleInputChange}
                  required
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Số điện thoại"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog} disabled={saving}>
              Hủy
            </Button>
            <Button 
              onClick={handleSaveEmployee} 
              variant="contained" 
              disabled={saving}
            >
              {saving ? <CircularProgress size={20} /> : (editingEmployee ? 'Cập nhật' : 'Thêm mới')}
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
