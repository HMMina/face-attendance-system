import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Box,
  AppBar,
  Toolbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  DatePicker,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Tabs,
  Tab,
  Divider
} from '@mui/material';
import {
  Assessment as ReportsIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  TrendingUp as TrendingUpIcon,
  Dashboard as DashboardIcon,
  GetApp as DownloadIcon,
  Schedule as ScheduleIcon,
  CalendarToday as CalendarIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`report-tabpanel-${index}`}
      aria-labelledby={`report-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

export default function AdvancedReports() {
  const [tabValue, setTabValue] = useState(0);
  const [reportType, setReportType] = useState('daily');
  const [dateRange, setDateRange] = useState('thisWeek');
  const [department, setDepartment] = useState('all');
  const [loading, setLoading] = useState(false);
  
  const [attendanceData, setAttendanceData] = useState([]);
  const [summaryStats, setSummaryStats] = useState({});
  const [departmentStats, setDepartmentStats] = useState([]);

  // Generate sample data
  const generateAttendanceData = () => {
    const employees = [
      'Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Thị D', 'Hoàng Văn E',
      'Vũ Thị F', 'Đặng Văn G', 'Bùi Thị H', 'Ngô Văn I', 'Lý Thị K'
    ];
    
    const data = employees.map((name, index) => ({
      id: index + 1,
      employee: name,
      department: ['IT', 'HR', 'Finance', 'Marketing'][index % 4],
      daysPresent: Math.floor(Math.random() * 5) + 18, // 18-22 days
      daysLate: Math.floor(Math.random() * 3), // 0-2 days
      daysAbsent: Math.floor(Math.random() * 3), // 0-2 days
      totalHours: Math.floor(Math.random() * 20) + 160, // 160-180 hours
      overtimeHours: Math.floor(Math.random() * 10), // 0-10 hours
      attendanceRate: Math.floor(Math.random() * 15) + 85 // 85-100%
    }));
    
    return data;
  };

  const generateSummaryStats = () => {
    return {
      totalEmployees: 45,
      averageAttendance: 92.5,
      totalWorkingDays: 22,
      totalHours: 7560,
      overtimeHours: 180,
      lateArrivals: 23,
      earlyDepartures: 15,
      absences: 12
    };
  };

  const generateDepartmentStats = () => {
    return [
      { name: 'IT', employees: 12, attendance: 94.2, avgHours: 175 },
      { name: 'HR', employees: 8, attendance: 89.5, avgHours: 168 },
      { name: 'Finance', employees: 15, attendance: 93.8, avgHours: 172 },
      { name: 'Marketing', employees: 10, attendance: 90.1, avgHours: 170 }
    ];
  };

  useEffect(() => {
    setAttendanceData(generateAttendanceData());
    setSummaryStats(generateSummaryStats());
    setDepartmentStats(generateDepartmentStats());
  }, []);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleGenerateReport = () => {
    setLoading(true);
    setTimeout(() => {
      setAttendanceData(generateAttendanceData());
      setSummaryStats(generateSummaryStats());
      setDepartmentStats(generateDepartmentStats());
      setLoading(false);
    }, 1500);
  };

  const handleExportReport = (format) => {
    // Simulate export
    alert(`Đang xuất báo cáo định dạng ${format}...`);
  };

  const getAttendanceColor = (rate) => {
    if (rate >= 95) return 'success';
    if (rate >= 85) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Navigation Bar */}
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            <ReportsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Báo cáo nâng cao
          </Typography>
          <Button color="inherit" component={Link} to="/dashboard" startIcon={<DashboardIcon />}>
            Dashboard
          </Button>
          <Button color="inherit" component={Link} to="/employees" startIcon={<PeopleIcon />}>
            Nhân viên
          </Button>
          <Button color="inherit" component={Link} to="/attendance" startIcon={<HistoryIcon />}>
            Chấm công
          </Button>
          <Button color="inherit" component={Link} to="/settings" startIcon={<SettingsIcon />}>
            Cài đặt
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {/* Report Controls */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Tùy chọn báo cáo
          </Typography>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Loại báo cáo</InputLabel>
                <Select
                  value={reportType}
                  label="Loại báo cáo"
                  onChange={(e) => setReportType(e.target.value)}
                >
                  <MenuItem value="daily">Hàng ngày</MenuItem>
                  <MenuItem value="weekly">Hàng tuần</MenuItem>
                  <MenuItem value="monthly">Hàng tháng</MenuItem>
                  <MenuItem value="quarterly">Quý</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Khoảng thời gian</InputLabel>
                <Select
                  value={dateRange}
                  label="Khoảng thời gian"
                  onChange={(e) => setDateRange(e.target.value)}
                >
                  <MenuItem value="thisWeek">Tuần này</MenuItem>
                  <MenuItem value="lastWeek">Tuần trước</MenuItem>
                  <MenuItem value="thisMonth">Tháng này</MenuItem>
                  <MenuItem value="lastMonth">Tháng trước</MenuItem>
                  <MenuItem value="thisQuarter">Quý này</MenuItem>
                  <MenuItem value="custom">Tùy chọn</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <FormControl fullWidth>
                <InputLabel>Phòng ban</InputLabel>
                <Select
                  value={department}
                  label="Phòng ban"
                  onChange={(e) => setDepartment(e.target.value)}
                >
                  <MenuItem value="all">Tất cả</MenuItem>
                  <MenuItem value="it">IT</MenuItem>
                  <MenuItem value="hr">HR</MenuItem>
                  <MenuItem value="finance">Finance</MenuItem>
                  <MenuItem value="marketing">Marketing</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Button
                variant="contained"
                fullWidth
                onClick={handleGenerateReport}
                disabled={loading}
                startIcon={<TrendingUpIcon />}
              >
                Tạo báo cáo
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Loading Indicator */}
        {loading && <LinearProgress sx={{ mb: 3 }} />}

        {/* Report Tabs */}
        <Paper sx={{ mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="report tabs">
            <Tab label="Tổng quan" icon={<TrendingUpIcon />} />
            <Tab label="Chi tiết nhân viên" icon={<PeopleIcon />} />
            <Tab label="Theo phòng ban" icon={<CalendarIcon />} />
            <Tab label="Thống kê" icon={<ScheduleIcon />} />
          </Tabs>

          {/* Overview Tab */}
          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Tổng nhân viên
                    </Typography>
                    <Typography variant="h4">
                      {summaryStats.totalEmployees}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Tỷ lệ chấm công TB
                    </Typography>
                    <Typography variant="h4">
                      {summaryStats.averageAttendance}%
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Tổng giờ làm
                    </Typography>
                    <Typography variant="h4">
                      {summaryStats.totalHours}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography color="textSecondary" gutterBottom>
                      Giờ tăng ca
                    </Typography>
                    <Typography variant="h4">
                      {summaryStats.overtimeHours}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Biểu đồ chấm công tuần (Giả lập)
                    </Typography>
                    <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.50' }}>
                      <Typography color="textSecondary">
                        Biểu đồ sẽ được hiển thị ở đây (cần thư viện Chart.js hoặc recharts)
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Employee Details Tab */}
          <TabPanel value={tabValue} index={1}>
            <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => handleExportReport('CSV')}
              >
                Xuất CSV
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => handleExportReport('Excel')}
              >
                Xuất Excel
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={() => handleExportReport('PDF')}
              >
                Xuất PDF
              </Button>
            </Box>

            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Nhân viên</TableCell>
                    <TableCell>Phòng ban</TableCell>
                    <TableCell>Ngày có mặt</TableCell>
                    <TableCell>Ngày muộn</TableCell>
                    <TableCell>Ngày vắng</TableCell>
                    <TableCell>Tổng giờ</TableCell>
                    <TableCell>Tăng ca</TableCell>
                    <TableCell>Tỷ lệ (%)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {attendanceData.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell>{row.employee}</TableCell>
                      <TableCell>
                        <Chip label={row.department} size="small" />
                      </TableCell>
                      <TableCell>{row.daysPresent}</TableCell>
                      <TableCell>{row.daysLate}</TableCell>
                      <TableCell>{row.daysAbsent}</TableCell>
                      <TableCell>{row.totalHours}h</TableCell>
                      <TableCell>{row.overtimeHours}h</TableCell>
                      <TableCell>
                        <Chip
                          label={`${row.attendanceRate}%`}
                          color={getAttendanceColor(row.attendanceRate)}
                          size="small"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </TabPanel>

          {/* Department Tab */}
          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              {departmentStats.map((dept) => (
                <Grid item xs={12} sm={6} md={3} key={dept.name}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {dept.name}
                      </Typography>
                      <Typography color="textSecondary">
                        Nhân viên: {dept.employees}
                      </Typography>
                      <Typography color="textSecondary">
                        Chấm công: {dept.attendance}%
                      </Typography>
                      <Typography color="textSecondary">
                        Giờ TB: {dept.avgHours}h
                      </Typography>
                      <Box sx={{ mt: 2 }}>
                        <LinearProgress
                          variant="determinate"
                          value={dept.attendance}
                          color={getAttendanceColor(dept.attendance)}
                          sx={{ height: 8, borderRadius: 1 }}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </TabPanel>

          {/* Statistics Tab */}
          <TabPanel value={tabValue} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Thống kê vi phạm
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>Đến muộn:</Typography>
                      <Typography>{summaryStats.lateArrivals} lần</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>Về sớm:</Typography>
                      <Typography>{summaryStats.earlyDepartures} lần</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Typography>Vắng mặt:</Typography>
                      <Typography>{summaryStats.absences} lần</Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      Xu hướng tháng này
                    </Typography>
                    <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'grey.50' }}>
                      <Typography color="textSecondary">
                        Biểu đồ xu hướng sẽ được hiển thị ở đây
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </TabPanel>
        </Paper>
      </Container>
    </Box>
  );
}
