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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Chip,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Snackbar,
  Avatar,
  Badge
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
  Work as WorkIcon,
  PhotoCamera as PhotoCameraIcon,
  CloudUpload as CloudUploadIcon
} from '@mui/icons-material';
import { getEmployees, getDepartments, addEmployee, addEmployeeWithPhoto, updateEmployee, uploadEmployeePhoto, deleteEmployee } from '../services/api';

export default function Employees() {
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]); // Ensure it's always an array
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
  const [customDepartment, setCustomDepartment] = useState('');
  
  // Photo upload states
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoUploading, setPhotoUploading] = useState(false);

  const savePhotoToBackend = async (file, employeeId) => {
    try {
      setPhotoUploading(true);
      console.log(`� Uploading photo for employee ${employeeId} to backend...`);
      
      const result = await uploadEmployeePhoto(employeeId, file);
      
      if (result.success) {
        console.log(`✅ Photo uploaded successfully for ${employeeId}`);
        console.log(`📁 Backend path: ${result.data.photo_path}`);
        console.log(`🌐 Photo URL: ${result.data.photo_url}`);
        return result.data.photo_url;
      } else {
        throw new Error(result.error || 'Failed to upload photo');
      }
    } catch (error) {
      console.error(`❌ Failed to upload photo for ${employeeId}:`, error);
      throw error;
    } finally {
      setPhotoUploading(false);
    }
  };

  const getEmployeePhotoUrl = (employee) => {
    // First check if employee has photo_path from backend
    if (employee.photo_path) {
      return `http://localhost:8000${employee.photo_path}`;
    }
    
    // Fallback: try backend API endpoint
    return `http://localhost:8000/api/v1/employees/${employee.employee_id}/photo`;
  };

  const fetchEmployees = async () => {
    try {
      setLoading(true);
      setError('');
      const result = await getEmployees();
      
      if (result.success) {
        // Sort employees by employee_id in ascending order
        const sortedEmployees = (result.data || []).sort((a, b) => {
          // Handle null/undefined employee_id values
          const idA = a.employee_id || '';
          const idB = b.employee_id || '';
          return idA.localeCompare(idB);
        });
        setEmployees(sortedEmployees);
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

  const fetchDepartments = async () => {
    try {
      const result = await getDepartments();
      if (result.success && Array.isArray(result.data)) {
        setDepartments(result.data);
      } else {
        // Fallback departments if API fails
        setDepartments(['IT Department', 'HR Department', 'Finance Department', 'Marketing Department']);
      }
    } catch (err) {
      console.error('Error fetching departments:', err);
      // Fallback departments - ensure it's always an array
      setDepartments(['IT Department', 'HR Department', 'Finance Department', 'Marketing Department']);
    }
  };

  useEffect(() => {
    fetchEmployees();
    fetchDepartments();
  }, []);

  const handleOpenDialog = (employee = null) => {
    if (employee) {
      setEditingEmployee(employee);
      const isCustomDept = !departments.includes(employee.department);
      setFormData({
        name: employee.name,
        email: employee.email,
        employee_id: employee.employee_id,
        department: isCustomDept ? 'custom' : employee.department,
        position: employee.position,
        phone: employee.phone
      });
      setCustomDepartment(isCustomDept ? employee.department : '');
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
      setCustomDepartment('');
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
    setCustomDepartment('');
    // Reset photo states
    setSelectedPhoto(null);
    setPhotoPreview(null);
    setPhotoUploading(false);
  };

  // Photo handling functions
  const handlePhotoSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError('Vui lòng chọn file ảnh (JPG, PNG, GIF...)');
        return;
      }
      
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        setError('Kích thước ảnh không được vượt quá 5MB');
        return;
      }
      
      setSelectedPhoto(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = () => {
    setSelectedPhoto(null);
    setPhotoPreview(null);
    // Reset file input
    const fileInput = document.getElementById('photo-upload-input');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const handleSaveEmployee = async () => {
    try {
      setSaving(true);
      setError('');
      
      // Validate required fields
      if (!formData.name.trim()) {
        throw new Error('Tên nhân viên là bắt buộc');
      }
      
      // Handle custom department
      const finalDepartment = formData.department === 'custom' ? customDepartment.trim() : formData.department;
      
      // Validate department if provided
      if (formData.department === 'custom' && !customDepartment.trim()) {
        throw new Error('Vui lòng nhập tên phòng ban tùy chỉnh');
      }
      
      // Validate email format if provided
      if (formData.email && !formData.email.includes('@')) {
        throw new Error('Email không đúng định dạng');
      }
      
      // Prepare final form data
      const finalFormData = {
        ...formData,
        department: finalDepartment
      };
      
      let result;
      if (editingEmployee) {
        // Update existing employee - use employee_id instead of id
        result = await updateEmployee(editingEmployee.employee_id, finalFormData);
        
        // Upload photo to backend if selected
        if (selectedPhoto && result.success) {
          try {
            await savePhotoToBackend(selectedPhoto, editingEmployee.employee_id);
          } catch (photoError) {
            console.warn('Failed to upload photo to backend:', photoError);
            setError('Cập nhật thông tin thành công nhưng upload ảnh thất bại');
          }
        }
      } else {
        // Add new employee
        if (selectedPhoto) {
          // Use addEmployeeWithPhoto API that handles both employee creation and photo upload
          const formDataWithPhoto = new FormData();
          formDataWithPhoto.append('name', finalFormData.name);
          formDataWithPhoto.append('email', finalFormData.email || '');
          formDataWithPhoto.append('employee_id', finalFormData.employee_id || '');
          formDataWithPhoto.append('department', finalFormData.department || '');
          formDataWithPhoto.append('position', finalFormData.position || '');
          formDataWithPhoto.append('phone', finalFormData.phone || '');
          formDataWithPhoto.append('photo', selectedPhoto);
          
          setPhotoUploading(true);
          result = await addEmployeeWithPhoto(formDataWithPhoto);
          setPhotoUploading(false);
        } else {
          // Add without photo
          result = await addEmployee(finalFormData);
        }
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
      setPhotoUploading(false);
    }
  };

  const handleDeleteEmployee = async (employee_id) => {
    if (window.confirm('Bạn có chắc chắn muốn xóa nhân viên này?')) {
      try {
        setError('');
        const result = await deleteEmployee(employee_id);
        
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

  const handleCustomDepartmentChange = (e) => {
    setCustomDepartment(e.target.value);
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
                  <TableCell>Ảnh</TableCell>
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
                    <TableCell>
                      <Avatar
                        src={getEmployeePhotoUrl(employee)}
                        alt={employee.name}
                        sx={{ width: 75, height: 75 }}
                      >
                        <PersonIcon />
                      </Avatar>
                    </TableCell>
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
                        onClick={() => handleDeleteEmployee(employee.employee_id)}
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
              {/* Photo Upload Section */}
              <Grid item xs={12}>
                <Box sx={{ textAlign: 'center', mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Ảnh nhân viên
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                    <Avatar
                      src={photoPreview || (editingEmployee ? getEmployeePhotoUrl(editingEmployee) : null)}
                      sx={{ width: 150, height: 150, bgcolor: 'grey.300' }}
                    >
                      <PhotoCameraIcon sx={{ fontSize: 60 }} />
                    </Avatar>
                    
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Button
                        variant="outlined"
                        component="label"
                        startIcon={<CloudUploadIcon />}
                        size="small"
                      >
                        Chọn ảnh
                        <input
                          type="file"
                          hidden
                          accept="image/*"
                          onChange={handlePhotoSelect}
                        />
                      </Button>
                      {(photoPreview || selectedPhoto) && (
                        <Button
                          variant="outlined"
                          color="error"
                          size="small"
                          onClick={() => {
                            setSelectedPhoto(null);
                            setPhotoPreview(null);
                          }}
                        >
                          Xóa ảnh
                        </Button>
                      )}
                    </Box>
                  </Box>
                </Box>
              </Grid>
              
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
                  helperText="Để trống để tự động tạo (EMP001, EMP002, ...)"
                  disabled={editingEmployee} // Không cho edit khi update
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
                  helperText="Email công ty của nhân viên"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel>Phòng ban</InputLabel>
                  <Select
                    value={formData.department}
                    label="Phòng ban"
                    name="department"
                    onChange={handleInputChange}
                  >
                    <MenuItem value="">
                      <em>Chọn phòng ban</em>
                    </MenuItem>
                    {Array.isArray(departments) && departments.map((dept, index) => (
                      <MenuItem key={index} value={dept}>
                        {dept}
                      </MenuItem>
                    ))}
                    <MenuItem value="custom">
                      <em>📝 Phòng ban khác (tùy chỉnh)</em>
                    </MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              {formData.department === 'custom' && (
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Tên phòng ban tùy chỉnh"
                    value={customDepartment}
                    onChange={handleCustomDepartmentChange}
                    required
                    helperText="Nhập tên phòng ban mới"
                    autoFocus
                  />
                </Grid>
              )}
              <Grid item xs={12} sm={6}>
                <TextField
                  fullWidth
                  label="Chức vụ"
                  name="position"
                  value={formData.position}
                  onChange={handleInputChange}
                  helperText="VD: Senior Developer, HR Manager, Marketing Specialist"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Số điện thoại"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  helperText="Số điện thoại liên hệ"
                />
              </Grid>
              
              {/* Photo Upload Section */}
              <Grid item xs={12}>
                <Card variant="outlined" sx={{ mt: 2 }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={1} mb={2}>
                      <PhotoCameraIcon color="primary" />
                      <Typography variant="h6">Upload ảnh thẻ nhân viên</Typography>
                    </Box>
                    
                    <Grid container spacing={2} alignItems="center">
                      <Grid item xs={12} sm={6}>
                        <input
                          accept="image/*"
                          style={{ display: 'none' }}
                          id="photo-upload-input"
                          type="file"
                          onChange={handlePhotoSelect}
                        />
                        <label htmlFor="photo-upload-input">
                          <Button
                            variant="outlined"
                            component="span"
                            startIcon={<CloudUploadIcon />}
                            fullWidth
                            disabled={photoUploading}
                          >
                            Chọn ảnh thẻ
                          </Button>
                        </label>
                        <Typography variant="caption" display="block" sx={{ mt: 1, color: 'text.secondary' }}>
                          Định dạng JPG, PNG. Tối đa 5MB
                        </Typography>
                      </Grid>
                      
                      {photoPreview && (
                        <Grid item xs={12} sm={6}>
                          <Box textAlign="center">
                            <Badge
                              overlap="circular"
                              anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
                              badgeContent={
                                <IconButton
                                  size="small"
                                  onClick={removePhoto}
                                  sx={{ 
                                    backgroundColor: 'error.main',
                                    color: 'white',
                                    '&:hover': { backgroundColor: 'error.dark' },
                                    width: 20,
                                    height: 20
                                  }}
                                >
                                  ×
                                </IconButton>
                              }
                            >
                              <Avatar
                                src={photoPreview}
                                sx={{ width: 120, height: 120, border: '2px solid #ddd' }}
                              />
                            </Badge>
                            <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                              {selectedPhoto?.name}
                            </Typography>
                          </Box>
                        </Grid>
                      )}
                      
                      {photoUploading && (
                        <Grid item xs={12}>
                          <Box display="flex" alignItems="center" gap={2}>
                            <CircularProgress size={20} />
                            <Typography variant="body2">Đang xử lý ảnh...</Typography>
                          </Box>
                        </Grid>
                      )}
                    </Grid>
                  </CardContent>
                </Card>
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
