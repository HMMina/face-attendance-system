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
import { getEmployees, getDepartments, addEmployee, addEmployeeWithPhoto, updateEmployee, uploadEmployeePhoto, uploadMultiplePhotos, deleteEmployee, api } from '../services/api';

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
  const [selectedPhotos, setSelectedPhotos] = useState([]); // Array of photos
  const [selectedAvatarIndex, setSelectedAvatarIndex] = useState(0); // Index of selected avatar
  const [photoUploading, setPhotoUploading] = useState(false);
  const [imageRefreshKey, setImageRefreshKey] = useState(0); // Key để force refresh ảnh
  
  // Search and filter states
  const [searchText, setSearchText] = useState('');
  const [filterDepartment, setFilterDepartment] = useState('');
  const [filteredEmployees, setFilteredEmployees] = useState([]);

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
      // Thêm timestamp và refresh key để tránh cache ảnh cũ
      return `http://localhost:8000${employee.photo_path}?v=${imageRefreshKey}&t=${Date.now()}`;
    }
    
    // Fallback: try backend API endpoint với timestamp và refresh key
    return `http://localhost:8000/api/v1/employees/${employee.employee_id}/photo?v=${imageRefreshKey}&t=${Date.now()}`;
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
      console.log('Departments API result:', result); // Debug log
      
      if (result.success && result.data) {
        // API trả về {departments: ["Marketing", "Kế toán", ...]}
        const deptArray = result.data.departments || result.data;
        if (Array.isArray(deptArray)) {
          setDepartments(deptArray);
          console.log('Departments loaded:', deptArray);
        } else {
          throw new Error('Invalid departments data format');
        }
      } else {
        throw new Error(result.error || 'Failed to fetch departments');
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

  // Filter employees based on search and department
  useEffect(() => {
    let filtered = employees;
    
    // Filter by search text (name or employee_id)
    if (searchText.trim()) {
      filtered = filtered.filter(emp => 
        emp.name.toLowerCase().includes(searchText.toLowerCase()) ||
        emp.employee_id.toLowerCase().includes(searchText.toLowerCase())
      );
    }
    
    // Filter by department
    if (filterDepartment) {
      filtered = filtered.filter(emp => emp.department === filterDepartment);
    }
    
    setFilteredEmployees(filtered);
  }, [employees, searchText, filterDepartment]);

  const handleOpenDialog = (employee = null) => {
    console.log('Opening dialog, current departments:', departments); // Debug log
    
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
    setSelectedPhotos([]);
    setSelectedAvatarIndex(0);
    setPhotoUploading(false);
  };

  // Photo handling functions
  const handlePhotoSelect = (event) => {
    const files = Array.from(event.target.files);
    
    if (files.length > 3) {
      setError('Chỉ được chọn tối đa 3 ảnh');
      return;
    }
    
    const validFiles = files.filter(file => {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setError(`File ${file.name} không phải là ảnh`);
        return false;
      }
      
      // Validate file size (5MB max)
      if (file.size > 5 * 1024 * 1024) {
        setError(`File ${file.name} quá lớn (tối đa 5MB)`);
        return false;
      }
      
      return true;
    });
    
    if (validFiles.length === 0) return;
    
    // Create preview URLs for selected photos
    const photoData = validFiles.map(file => ({
      file: file,
      preview: URL.createObjectURL(file),
      name: file.name
    }));
    
    setSelectedPhotos(photoData);
    setSelectedAvatarIndex(0); // Default to first photo as avatar
  };

  const removePhoto = (index) => {
    const newPhotos = selectedPhotos.filter((_, i) => i !== index);
    setSelectedPhotos(newPhotos);
    
    // Adjust avatar index if needed
    if (selectedAvatarIndex >= newPhotos.length) {
      setSelectedAvatarIndex(Math.max(0, newPhotos.length - 1));
    }
    
    // Reset file input if no photos left
    if (newPhotos.length === 0) {
      const fileInput = document.getElementById('photo-upload-input');
      if (fileInput) {
        fileInput.value = '';
      }
    }
  };

  const selectAvatar = (index) => {
    setSelectedAvatarIndex(index);
  };

  const handleDeleteCurrentAvatar = async () => {
    if (!editingEmployee) return;
    
    if (window.confirm('Bạn có chắc chắn muốn xóa ảnh hiện tại của nhân viên này?')) {
      try {
        setPhotoUploading(true);
        
        // Call API to delete current photo
        const result = await api.delete(`/employees/${editingEmployee.employee_id}/photo`);
        
        if (result.status === 200) {
          setSuccess('Xóa ảnh thành công!');
          setImageRefreshKey(prev => prev + 1);
          await fetchEmployees();
        } else {
          throw new Error('Failed to delete photo');
        }
      } catch (error) {
        console.error('Delete photo error:', error);
        setError('Không thể xóa ảnh. Vui lòng thử lại.');
      } finally {
        setPhotoUploading(false);
      }
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
        if (selectedPhotos.length > 0 && result.success) {
          try {
            if (selectedPhotos.length === 1) {
              // Upload single photo as avatar
              const avatarPhoto = selectedPhotos[0];
              await savePhotoToBackend(avatarPhoto.file, editingEmployee.employee_id);
            } else {
              // Upload multiple photos with selected avatar index
              const photoFiles = selectedPhotos.map(photo => photo.file);
              console.log(`🚀 DEBUG: Starting multiple photos upload for employee ${editingEmployee.employee_id}`);
              console.log(`📸 DEBUG: Photo count: ${photoFiles.length}, Avatar index: ${selectedAvatarIndex}`);
              console.log('📋 DEBUG: Photo files:', photoFiles.map(f => ({ name: f.name, size: f.size, type: f.type })));
              
              const uploadResult = await uploadMultiplePhotos(
                editingEmployee.employee_id, 
                photoFiles, 
                selectedAvatarIndex
              );
              
              console.log('📡 DEBUG: Upload result:', uploadResult);
              
              if (!uploadResult.success) {
                throw new Error(uploadResult.error || 'Failed to upload multiple photos');
              }
              
              console.log(`✅ Uploaded ${selectedPhotos.length} photos, avatar index: ${selectedAvatarIndex}`);
            }
            
            // Force refresh ảnh bằng cách tăng refresh key
            setImageRefreshKey(prev => prev + 1);
            
            // Refresh employee list để cập nhật ảnh mới
            await fetchEmployees();
            console.log('✅ Photo updated and employee list refreshed');
          } catch (photoError) {
            console.warn('Failed to upload photo to backend:', photoError);
            setError('Cập nhật thông tin thành công nhưng upload ảnh thất bại: ' + photoError.message);
          }
        }
      } else {
        // Add new employee
        if (selectedPhotos.length > 0) {
          // Use addEmployeeWithPhoto API that handles both employee creation and photo upload
          const formDataWithPhoto = new FormData();
          formDataWithPhoto.append('name', finalFormData.name);
          formDataWithPhoto.append('email', finalFormData.email || '');
          formDataWithPhoto.append('employee_id', finalFormData.employee_id || '');
          formDataWithPhoto.append('department', finalFormData.department || '');
          formDataWithPhoto.append('position', finalFormData.position || '');
          formDataWithPhoto.append('phone', finalFormData.phone || '');
          
          // Upload the selected avatar photo
          const avatarPhoto = selectedPhotos[selectedAvatarIndex];
          formDataWithPhoto.append('photo', avatarPhoto.file);
          
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
        
        // Force refresh ảnh nếu có upload ảnh
        if (selectedPhotos.length > 0) {
          setImageRefreshKey(prev => prev + 1);
        }
        
        handleCloseDialog();
        
        // Luôn refresh danh sách để cập nhật ảnh mới
        await fetchEmployees();
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
    if (!department) return 'default';
    
    // Tạo hash từ tên phòng ban để đảm bảo màu khác nhau cho mỗi phòng
    let hash = 0;
    for (let i = 0; i < department.length; i++) {
      const char = department.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    
    // Bảng màu dễ nhìn, dễ phân biệt
    const colors = [
      'primary',    // Xanh dương
      'secondary',  // Tím
      'success',    // Xanh lá
      'warning',    // Cam
      'error',      // Đỏ
      'info'        // Xanh nhạt
    ];
    
    // Sử dụng hash để chọn màu, đảm bảo cùng tên luôn có cùng màu
    const colorIndex = Math.abs(hash) % colors.length;
    return colors[colorIndex];
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

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}> {/* Tăng từ lg lên xl để rộng hơn */}
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
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <WorkIcon color="info" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Tổng phòng ban
                    </Typography>
                    <Typography variant="h5">
                      {departments.length}
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
                  <PersonIcon color="warning" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Không hoạt động
                    </Typography>
                    <Typography variant="h5">
                      {employees.filter(emp => !emp.is_active).length}
                    </Typography>
                  </Box>
                </Box>
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

        {/* Search and Filter Section */}
        <Paper sx={{ p: 2, mb: 3 }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <TextField
                fullWidth
                label="Tìm kiếm theo tên hoặc mã NV"
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Nhập tên hoặc mã nhân viên..."
                size="small"
              />
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Lọc theo phòng ban</InputLabel>
                <Select
                  value={filterDepartment}
                  label="Lọc theo phòng ban"
                  onChange={(e) => setFilterDepartment(e.target.value)}
                >
                  <MenuItem value="">Tất cả phòng ban</MenuItem>
                  {departments.map((dept, index) => (
                    <MenuItem key={index} value={dept}>
                      {dept}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={12} md={5}>
              <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                <Typography variant="body2" color="text.secondary">
                  Hiển thị: {filteredEmployees.length} / {employees.length} nhân viên
                </Typography>
                {(searchText || filterDepartment) && (
                  <Button
                    size="small"
                    onClick={() => {
                      setSearchText('');
                      setFilterDepartment('');
                    }}
                  >
                    Xóa bộ lọc
                  </Button>
                )}
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Employees Table */}
        <Paper sx={{ width: '100%', overflow: 'auto' }}>
          <TableContainer sx={{ maxHeight: '75vh' }}> {/* Bỏ minWidth để table tự động fit */}
            <Table stickyHeader size="small"> {/* Thêm size="small" để compact hơn */}
              <TableHead>
                <TableRow>
                  <TableCell sx={{ width: '120px', textAlign: 'center' }}>Ảnh</TableCell>
                  <TableCell sx={{ width: '120px', textAlign: 'center' }}>Mã NV</TableCell>
                  <TableCell sx={{ width: '200px', textAlign: 'center' }}>Họ tên</TableCell>
                  <TableCell sx={{ width: '150px', textAlign: 'center' }}>Phòng ban</TableCell>
                  <TableCell sx={{ width: '180px', textAlign: 'center' }}>Chức vụ</TableCell>
                  <TableCell sx={{ width: '130px', textAlign: 'center' }}>Điện thoại</TableCell>
                  <TableCell sx={{ width: '220px', textAlign: 'center' }}>Email</TableCell>
                  <TableCell sx={{ width: '100px', textAlign: 'center' }}>Trạng thái</TableCell>
                  <TableCell sx={{ width: '100px', textAlign: 'center' }}>Thao tác</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredEmployees.map((employee) => (
                  <TableRow key={employee.id}>
                    {/* Ảnh */}
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Avatar
                        src={getEmployeePhotoUrl(employee)}
                        alt={employee.name}
                        sx={{ width: 100, height: 100, margin: '0 auto' }}
                      >
                        <PersonIcon />
                      </Avatar>
                    </TableCell>
                    {/* Mã NV */}
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                        {employee.employee_id}
                      </Typography>
                    </TableCell>
                    {/* Họ tên */}
                    <TableCell>
                      <Box sx={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        overflow: 'hidden'
                      }}>
                        <PersonIcon sx={{ mr: 1, color: 'text.secondary', flexShrink: 0 }} />
                        <Typography 
                          variant="body2" 
                          title={employee.name}
                          sx={{ 
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {employee.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    {/* Phòng ban */}
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Chip
                        label={employee.department}
                        color={getDepartmentColor(employee.department)}
                        size="small"
                      />
                    </TableCell>
                    {/* Chức vụ */}
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontSize: '0.875rem',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                        title={employee.position}
                      >
                        {employee.position}
                      </Typography>
                    </TableCell>
                    {/* Điện thoại */}
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                        {employee.phone}
                      </Typography>
                    </TableCell>
                    {/* Email */}
                    <TableCell>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          fontSize: '0.875rem',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}
                        title={employee.email}
                      >
                        {employee.email}
                      </Typography>
                    </TableCell>
                    {/* Trạng thái */}
                    <TableCell sx={{ textAlign: 'center' }}>
                      <Chip
                        label={getStatusText(employee.is_active)}
                        color={getStatusColor(employee.is_active)}
                        size="small"
                      />
                    </TableCell>
                    {/* Thao tác */}
                    <TableCell sx={{ textAlign: 'center' }}>
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
                    Ảnh nhân viên (Tối đa 3 ảnh)
                  </Typography>
                  
                  {/* Selected Avatar Preview */}
                  <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
                    <Avatar
                      src={selectedPhotos.length > 0 ? selectedPhotos[selectedAvatarIndex]?.preview : 
                           (editingEmployee ? getEmployeePhotoUrl(editingEmployee) : null)}
                      sx={{ width: 150, height: 150, bgcolor: 'grey.300', border: '3px solid #2196f3' }}
                    >
                      <PhotoCameraIcon sx={{ fontSize: 60 }} />
                    </Avatar>
                    <Typography variant="caption" color="primary">
                      Avatar hiển thị
                    </Typography>
                  </Box>
                  
                  {/* Photo Selection Grid */}
                  {selectedPhotos.length > 0 && (
                    <Box sx={{ mt: 2, mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Chọn ảnh làm avatar:
                      </Typography>
                      <Grid container spacing={1} justifyContent="center">
                        {selectedPhotos.map((photo, index) => (
                          <Grid item key={index}>
                            <Box sx={{ position: 'relative' }}>
                              <Avatar
                                src={photo.preview}
                                sx={{ 
                                  width: 80, 
                                  height: 80, 
                                  cursor: 'pointer',
                                  border: selectedAvatarIndex === index ? '3px solid #2196f3' : '2px solid #ddd',
                                  opacity: selectedAvatarIndex === index ? 1 : 0.7
                                }}
                                onClick={() => selectAvatar(index)}
                              />
                              {selectedAvatarIndex === index && (
                                <Box sx={{
                                  position: 'absolute',
                                  top: -5,
                                  right: -5,
                                  bgcolor: 'primary.main',
                                  color: 'white',
                                  borderRadius: '50%',
                                  width: 20,
                                  height: 20,
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  fontSize: 12
                                }}>
                                  ✓
                                </Box>
                              )}
                              <IconButton
                                size="small"
                                onClick={() => removePhoto(index)}
                                sx={{ 
                                  position: 'absolute',
                                  top: -10,
                                  left: -10,
                                  backgroundColor: 'error.main',
                                  color: 'white',
                                  '&:hover': { backgroundColor: 'error.dark' },
                                  width: 20,
                                  height: 20
                                }}
                              >
                                ×
                              </IconButton>
                            </Box>
                          </Grid>
                        ))}
                      </Grid>
                    </Box>
                  )}
                  
                  <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                    <Button
                      variant="outlined"
                      component="label"
                      startIcon={<CloudUploadIcon />}
                      size="small"
                      disabled={selectedPhotos.length >= 3}
                    >
                      {selectedPhotos.length === 0 ? 'Chọn ảnh' : `Thêm ảnh (${selectedPhotos.length}/3)`}
                      <input
                        type="file"
                        hidden
                        accept="image/*"
                        multiple
                        max="3"
                        onChange={handlePhotoSelect}
                      />
                    </Button>
                    {selectedPhotos.length > 0 && (
                      <Button
                        variant="outlined"
                        color="error"
                        size="small"
                        onClick={() => setSelectedPhotos([])}
                      >
                        Xóa tất cả
                      </Button>
                    )}
                    {editingEmployee && (
                      <Button
                        variant="outlined"
                        color="warning"
                        size="small"
                        onClick={handleDeleteCurrentAvatar}
                      >
                        Xóa ảnh hiện tại
                      </Button>
                    )}
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
