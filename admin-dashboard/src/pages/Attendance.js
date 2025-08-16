import React, { useState, useEffect } from 'react';
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
  TextField,
  Box,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  AppBar,
  Toolbar
} from '@mui/material';
import {
  AccessTime as TimeIcon,
  Person as PersonIcon,
  DevicesOther as DeviceIcon,
  Search as SearchIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
  Today as TodayIcon,
  Home as HomeIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Assessment as ReportsIcon
} from '@mui/icons-material';
import { Link } from 'react-router-dom';
import { getAllAttendance, getEmployees } from '../services/api';
import { getCurrentDateString, formatDateFromTimestamp, formatTimeFromTimestamp, isLateCheckIn } from '../utils/dateUtils';

export default function Attendance() {
  const [attendanceData, setAttendanceData] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEmployee, setSelectedEmployee] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const fetchAttendanceData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch employees and attendance data
      const [employeesResult, attendanceResult] = await Promise.all([
        getEmployees(),
        getAllAttendance()
      ]);

      if (employeesResult.success) {
        setEmployees(employeesResult.data || []);
      }

      if (attendanceResult.success) {
        const rawData = attendanceResult.data || [];
        const employeeList = employeesResult.success ? (employeesResult.data || []) : [];
        
        // Group attendance records by employee and date
        const groupedData = {};
        rawData.forEach(record => {
          const date = record.timestamp ? record.timestamp.split('T')[0] : '';
          const key = `${record.employee_id}_${date}`;
          
          if (!groupedData[key]) {
            groupedData[key] = {
              employee_id: record.employee_id,
              date: date,
              records: []
            };
          }
          groupedData[key].records.push(record);
        });
        
        // Transform grouped data to attendance entries
        const transformedData = Object.values(groupedData).map((group, index) => {
          // Find employee name by employee_id (string matching)
          const employee = employeeList.find(emp => emp.employee_id === group.employee_id);
          const employeeName = employee ? employee.name : `Employee #${group.employee_id}`;
          
          // Sort records by timestamp to get first (check-in) and last (check-out)
          const sortedRecords = group.records.sort((a, b) => 
            new Date(a.timestamp) - new Date(b.timestamp)
          );
          
          const firstRecord = sortedRecords[0];
          const lastRecord = sortedRecords[sortedRecords.length - 1];
          
          const checkInTime = firstRecord ? new Date(firstRecord.timestamp) : null;
          // Only set check-out if there are multiple records AND they're different times
          const checkOutTime = sortedRecords.length > 1 && lastRecord && 
            firstRecord.timestamp !== lastRecord.timestamp ? 
            new Date(lastRecord.timestamp) : null;
          
          // Calculate working hours
          let hoursWorked = '0.0';
          if (checkInTime && checkOutTime && checkInTime.getTime() !== checkOutTime.getTime()) {
            const diffMs = checkOutTime - checkInTime;
            const diffHours = diffMs / (1000 * 60 * 60);
            hoursWorked = diffHours > 0 ? diffHours.toFixed(1) : '0.0';
          }
          
          // Determine status based on check-in time
          let status = 'present';
          if (checkInTime) {
            status = isLateCheckIn(firstRecord.timestamp) ? 'late' : 'present';
          }
          
          return {
            id: index + 1,
            employeeName: employeeName,
            employeeId: group.employee_id,
            date: group.date,
            checkIn: checkInTime ? formatTimeFromTimestamp(firstRecord.timestamp) : '',
            checkOut: checkOutTime ? formatTimeFromTimestamp(lastRecord.timestamp) : '',
            status: status,
            hoursWorked: hoursWorked
          };
        });

        setAttendanceData(transformedData);
      } else {
        throw new Error(attendanceResult.error || 'Failed to fetch attendance data');
      }
    } catch (err) {
      console.error('❌ Error fetching attendance data:', err);
      setError(err.message || 'Không thể tải dữ liệu chấm công từ database');
      setAttendanceData([]); // Don't fallback to sample data
    } finally {
      setLoading(false);
    }
  };

  const getAttendanceStatus = (record) => {
    if (!record.check_in_time) return 'absent';
    
    try {
      const checkInTime = new Date(record.check_in_time);
      if (isNaN(checkInTime.getTime())) return 'absent';
      
      const workStartTime = new Date(checkInTime);
      workStartTime.setHours(8, 0, 0, 0); // Assume work starts at 8:00 AM
      
      return checkInTime > workStartTime ? 'late' : 'present';
    } catch (error) {
      console.error('Error getting attendance status:', error);
      return 'absent';
    }
  };

  const calculateHoursWorked = (checkIn, checkOut) => {
    if (!checkIn || !checkOut) return '0.0';
    
    try {
      const start = new Date(checkIn);
      const end = new Date(checkOut);
      
      // Check if dates are valid
      if (isNaN(start.getTime()) || isNaN(end.getTime())) {
        return '0.0';
      }
      
      const diffMs = end - start;
      const diffHours = diffMs / (1000 * 60 * 60);
      
      return diffHours > 0 ? diffHours.toFixed(1) : '0.0';
    } catch (error) {
      console.error('Error calculating hours worked:', error);
      return '0.0';
    }
  };

  useEffect(() => {
    fetchAttendanceData();
    
    // Refresh every 30 seconds for real-time updates
    const interval = setInterval(fetchAttendanceData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Calculate statistics for today
  const today = getCurrentDateString();
  const todayRecords = attendanceData.filter(a => a.date === today);
  const presentToday = todayRecords.filter(a => a.status === 'present').length;
  const lateToday = todayRecords.filter(a => a.status === 'late').length;
  const totalEmployees = employees.length;
  const absentToday = totalEmployees > 0 ? Math.max(0, totalEmployees - todayRecords.length) : 0;

  const exportToCSV = () => {
    const headers = ['Tên nhân viên', 'Ngày', 'Giờ vào', 'Giờ ra', 'Trạng thái', 'Giờ làm việc'];
    const csvContent = [
      headers.join(','),
      ...attendanceData.map(row => [
        row.employeeName,
        row.date,
        row.checkIn,
        row.checkOut,
        row.status,
        row.hoursWorked
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'attendance-report.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'present': return 'success';
      case 'late': return 'warning';
      case 'absent': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'present': return 'Có mặt';
      case 'late': return 'Muộn';
      case 'absent': return 'Vắng';
      default: return status;
    }
  };

  return (
    <Box>
      {/* Navigation Bar */}
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Lịch sử chấm công
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
        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <TodayIcon color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Hôm nay
                    </Typography>
                    <Typography variant="h6">
                      {todayRecords.length}
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
                  <PersonIcon color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Có mặt
                    </Typography>
                    <Typography variant="h6">
                      {presentToday}
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
                  <TimeIcon color="warning" sx={{ mr: 1 }} />
                  <Box>
                    <Typography color="textSecondary" gutterBottom>
                      Muộn
                    </Typography>
                    <Typography variant="h6">
                      {lateToday}
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
                      Vắng
                    </Typography>
                    <Typography variant="h6">
                      {absentToday}
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filters */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Bộ lọc
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <TextField
                fullWidth
                label="Tìm kiếm nhân viên"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                type="date"
                label="Từ ngày"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <TextField
                fullWidth
                type="date"
                label="Đến ngày"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <FormControl fullWidth>
                <InputLabel>Nhân viên</InputLabel>
                <Select
                  value={selectedEmployee}
                  label="Nhân viên"
                  onChange={(e) => setSelectedEmployee(e.target.value)}
                >
                  <MenuItem value="">Tất cả</MenuItem>
                  <MenuItem value="1">Nguyễn Văn A</MenuItem>
                  <MenuItem value="2">Trần Thị B</MenuItem>
                  <MenuItem value="3">Lê Văn C</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="contained"
                  onClick={handleSearch}
                  startIcon={<SearchIcon />}
                  disabled={loading}
                >
                  Tìm kiếm
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => setLoading(true)}
                  startIcon={<RefreshIcon />}
                  disabled={loading}
                >
                  Làm mới
                </Button>
                <Button
                  variant="outlined"
                  onClick={exportToCSV}
                  startIcon={<DownloadIcon />}
                  disabled={loading}
                >
                  Xuất CSV
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Attendance Table */}
        <Paper>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">
              Danh sách chấm công
            </Typography>
          </Box>
          
          {error && (
            <Alert severity="error" sx={{ m: 2 }}>
              {error}
            </Alert>
          )}
          
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>STT</TableCell>
                    <TableCell>Tên nhân viên</TableCell>
                    <TableCell>Ngày</TableCell>
                    <TableCell>Giờ vào</TableCell>
                    <TableCell>Giờ ra</TableCell>
                    <TableCell>Giờ làm việc</TableCell>
                    <TableCell>Trạng thái</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendanceData
                    .filter(item => 
                      searchTerm === '' || 
                      item.employeeName.toLowerCase().includes(searchTerm.toLowerCase())
                    )
                    .slice(0, 15)
                    .map((row, index) => (
                    <TableRow key={row.id}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>{row.employeeName}</TableCell>
                      <TableCell>{row.date}</TableCell>
                      <TableCell>{row.checkIn}</TableCell>
                      <TableCell>{row.checkOut}</TableCell>
                      <TableCell>{row.hoursWorked}h</TableCell>
                      <TableCell>
                        <Chip
                          label={getStatusText(row.status)}
                          color={getStatusColor(row.status)}
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
      </Container>
    </Box>
  );
}
