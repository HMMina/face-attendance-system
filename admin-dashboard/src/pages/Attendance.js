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
  Assessment as ReportsIcon,
  Devices as DevicesIcon
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
        
        console.log(`📊 DEBUG: Fetched ${rawData.length} attendance records`);
        console.log('🔍 Sample records:', rawData.slice(0, 3));
        
        // Group attendance records by employee and date
        const groupedData = {};
        rawData.forEach(record => {
          // Handle timestamp parsing - database format: "2025-09-04 18:11:08.738343"
          let date = '';
          if (record.timestamp) {
            try {
              // Parse timestamp to extract date in YYYY-MM-DD format
              const timestamp = record.timestamp;
              
              if (timestamp.includes('T')) {
                // ISO format: "2025-09-04T18:11:08.738343"
                date = timestamp.split('T')[0];
              } else if (timestamp.includes(' ')) {
                // Space format: "2025-09-04 18:11:08.738343"
                date = timestamp.split(' ')[0];
              } else {
                // Try parsing as Date object
                const parsedDate = new Date(timestamp);
                if (!isNaN(parsedDate.getTime())) {
                  date = parsedDate.toISOString().split('T')[0];
                }
              }
              
              console.log(`📅 DEBUG: Processing timestamp "${record.timestamp}" -> date: "${date}"`);
            } catch (e) {
              console.error(`❌ Failed to parse timestamp: ${record.timestamp}`, e);
              date = '';
            }
          }
          
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
          
          // Sort records by timestamp
          const sortedRecords = group.records.sort((a, b) => 
            new Date(a.timestamp) - new Date(b.timestamp)
          );
          
          // Improved logic: Find FIRST CHECK_IN and LAST CHECK_OUT for the day
          const checkInRecords = sortedRecords.filter(record => record.action_type === 'CHECK_IN');
          const checkOutRecords = sortedRecords.filter(record => record.action_type === 'CHECK_OUT');
          
          const checkInRecord = checkInRecords.length > 0 ? checkInRecords[0] : null; // First CHECK_IN
          const checkOutRecord = checkOutRecords.length > 0 ? checkOutRecords[checkOutRecords.length - 1] : null; // Last CHECK_OUT
          
          const checkInTime = checkInRecord ? new Date(checkInRecord.timestamp) : null;
          const checkOutTime = checkOutRecord ? new Date(checkOutRecord.timestamp) : null;
          
          // Debug logging for attendance logic
          if (group.records.length > 2) {
            console.log(`🕐 DEBUG: Employee ${group.employee_id} on ${group.date}:`);
            console.log(`   Records count: ${group.records.length}`);
            console.log(`   CHECK_IN count: ${checkInRecords.length}`);
            console.log(`   CHECK_OUT count: ${checkOutRecords.length}`);
            console.log(`   First CHECK_IN: ${checkInRecord?.timestamp}`);
            console.log(`   Last CHECK_OUT: ${checkOutRecord?.timestamp}`);
          }
          
          // Calculate working hours
          let hoursWorked = '0.0';
          if (checkInTime && checkOutTime) {
            const diffMs = checkOutTime - checkInTime;
            const diffHours = diffMs / (1000 * 60 * 60);
            hoursWorked = diffHours > 0 ? diffHours.toFixed(1) : '0.0';
          }
          
          // Determine status based on check-in time
          let status = 'present';
          if (checkInTime) {
            status = isLateCheckIn(checkInRecord.timestamp) ? 'late' : 'present';
          }
          
          return {
            id: index + 1,
            employeeName: employeeName,
            employeeId: group.employee_id,
            date: group.date,
            checkIn: checkInTime ? formatTimeFromTimestamp(checkInRecord.timestamp) : '',
            checkOut: checkOutTime ? formatTimeFromTimestamp(checkOutRecord.timestamp) : '',
            deviceId: checkInRecord ? checkInRecord.device_id : (checkOutRecord ? checkOutRecord.device_id : 'N/A'),
            status: status,
            hoursWorked: hoursWorked
          };
        });

        console.log(`📋 DEBUG: Transformed to ${transformedData.length} attendance entries`);
        console.log('📅 Date range in data:', {
          allDates: [...new Set(transformedData.map(d => d.date))].sort(),
          earliest: transformedData.length > 0 ? Math.min(...transformedData.map(d => d.date)) : 'none',
          latest: transformedData.length > 0 ? Math.max(...transformedData.map(d => d.date)) : 'none'
        });
        console.log('🔍 Sample transformed data:', transformedData.slice(0, 5));
        console.log('🔍 All unique dates in dataset:', [...new Set(transformedData.map(d => d.date))].sort());

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
    
    // Remove auto-refresh to prevent page from reloading while user is viewing data
    // Users can manually refresh using the "Làm mới" button if needed
    // const interval = setInterval(fetchAttendanceData, 30000);
    // return () => clearInterval(interval);
  }, []);

  // Calculate statistics for today
  const today = getCurrentDateString();
  const todayRecords = attendanceData.filter(a => a.date === today);
  const presentToday = todayRecords.filter(a => a.status === 'present').length;
  const lateToday = todayRecords.filter(a => a.status === 'late').length;
  const totalEmployees = employees.length;
  const absentToday = totalEmployees > 0 ? Math.max(0, totalEmployees - todayRecords.length) : 0;

  const exportToCSV = () => {
    // Get filtered data that matches current display (same logic as table rendering)
    const filteredData = attendanceData.filter(item => {
      // Search filter
      const matchesSearch = searchTerm === '' || 
        item.employeeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.employeeId.toLowerCase().includes(searchTerm.toLowerCase());
      
      // Employee filter
      const matchesEmployee = selectedEmployee === '' || 
        item.employeeId === selectedEmployee;
      
      // Date range filter
      let matchesDateRange = true;
      if (startDate || endDate) {
        matchesDateRange = (!startDate || item.date >= startDate) && 
          (!endDate || item.date <= endDate);
      }
      
      return matchesSearch && matchesEmployee && matchesDateRange;
    });

    if (filteredData.length === 0) {
      alert('Không có dữ liệu để xuất file CSV!');
      return;
    }

    const headers = ['STT', 'Mã NV', 'Tên nhân viên', 'Ngày', 'Giờ vào', 'Giờ ra', 'Giờ làm việc', 'Thiết bị'];
    const csvContent = [
      headers.join(','),
      ...filteredData.map((row, index) => [
        index + 1, // STT
        row.employeeId, // Mã NV
        `"${row.employeeName}"`, // Wrap in quotes to handle commas in names
        row.date,
        row.checkIn,
        row.checkOut,
        row.hoursWorked,
        row.deviceId || 'N/A'
      ].join(','))
    ].join('\n');

    // Add BOM for UTF-8 encoding to display Vietnamese correctly in Excel
    const BOM = '\uFEFF';
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    // Create dynamic filename based on filters
    let filename = 'attendance-report';
    if (startDate && endDate) {
      filename += `_${startDate}_to_${endDate}`;
    } else if (startDate) {
      filename += `_from_${startDate}`;
    } else if (endDate) {
      filename += `_to_${endDate}`;
    } else {
      filename += `_${getCurrentDateString()}`;
    }
    if (selectedEmployee) {
      filename += `_${selectedEmployee}`;
    }
    filename += '.csv';
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Show success message
    alert(`Đã xuất ${filteredData.length} bản ghi ra file CSV: ${filename}`);
  };

  const handleSearch = () => {
    // Validate date range
    if (startDate && endDate && startDate > endDate) {
      setError('Ngày bắt đầu không thể lớn hơn ngày kết thúc');
      return;
    }
    
    // Clear any previous errors
    setError('');
    
    // Apply filters by re-fetching data with current filter parameters
    // The actual filtering is done in the render method
    // This function serves as a trigger for search action
    console.log('🔍 Searching with filters:', {
      searchTerm,
      selectedEmployee,
      startDate,
      endDate
    });
    
    // Optionally refresh data
    if (searchTerm || selectedEmployee || startDate || endDate) {
      fetchAttendanceData();
    }
  };

  const handleClearFilters = () => {
    setSearchTerm('');
    setSelectedEmployee('');
    // Set to today's date instead of empty
    const today = getCurrentDateString();
    setStartDate(today);
    setEndDate(today);
    setError('');
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
          <Button color="inherit" component={Link} to="/devices" startIcon={<DevicesIcon />}>
            Thiết bị
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
                label="Tìm kiếm theo tên hoặc mã NV"
                placeholder="Nhập tên hoặc mã nhân viên..."
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
                <InputLabel>Mã nhân viên</InputLabel>
                <Select
                  value={selectedEmployee}
                  label="Mã nhân viên"
                  onChange={(e) => setSelectedEmployee(e.target.value)}
                >
                  <MenuItem value="">Tất cả</MenuItem>
                  {employees.map((employee) => (
                    <MenuItem key={employee.employee_id} value={employee.employee_id}>
                      {employee.employee_id} - {employee.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
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
                  onClick={handleClearFilters}
                  disabled={loading}
                  sx={{ minWidth: 'auto' }}
                >
                  Xóa bộ lọc
                </Button>
                <Button
                  variant="outlined"
                  onClick={fetchAttendanceData}
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
                    <TableCell>Mã NV</TableCell>
                    <TableCell>Tên nhân viên</TableCell>
                    <TableCell>Ngày</TableCell>
                    <TableCell>Giờ vào</TableCell>
                    <TableCell>Giờ ra</TableCell>
                    <TableCell>Giờ làm việc</TableCell>
                    <TableCell>Thiết bị</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendanceData
                    .filter(item => {
                      // Search term filter - tìm theo tên hoặc mã nhân viên
                      const matchesSearch = searchTerm === '' || 
                        item.employeeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        item.employeeId.toLowerCase().includes(searchTerm.toLowerCase());
                      
                      // Employee filter
                      const matchesEmployee = selectedEmployee === '' || 
                        item.employeeId === selectedEmployee;
                      
                      // Date range filter - ENHANCED DEBUG
                      let matchesDateRange = true;
                      if (startDate || endDate) {
                        // item.date format: "2025-09-05"
                        // startDate/endDate format: "2025-09-01"
                        
                        console.log(`🔍 DETAILED DATE CHECK for ${item.employeeId} (${item.employeeName}):`, {
                          itemDate: item.date,
                          startDate: startDate,
                          endDate: endDate,
                          startComparison: startDate ? `${item.date} >= ${startDate} = ${item.date >= startDate}` : 'no startDate',
                          endComparison: endDate ? `${item.date} <= ${endDate} = ${item.date <= endDate}` : 'no endDate'
                        });
                        
                        // String comparison for YYYY-MM-DD format
                        const startCheck = !startDate || item.date >= startDate;
                        const endCheck = !endDate || item.date <= endDate;
                        matchesDateRange = startCheck && endCheck;
                        
                        console.log(`   🎯 Final result: startCheck=${startCheck}, endCheck=${endCheck}, matchesDateRange=${matchesDateRange}`);
                      }
                      
                      const finalMatch = matchesSearch && matchesEmployee && matchesDateRange;
                      
                      return finalMatch;
                    })
                    .map((row, index) => (
                    <TableRow key={row.id}>
                      <TableCell>{index + 1}</TableCell>
                      <TableCell>{row.employeeId}</TableCell>
                      <TableCell>{row.employeeName}</TableCell>
                      <TableCell>{row.date}</TableCell>
                      <TableCell>{row.checkIn}</TableCell>
                      <TableCell>{row.checkOut}</TableCell>
                      <TableCell>{row.hoursWorked}h</TableCell>
                      <TableCell>{row.deviceId || 'N/A'}</TableCell>
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
