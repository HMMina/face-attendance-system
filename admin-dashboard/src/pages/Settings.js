import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Paper,
  Typography,
  Button,
  TextField,
  Box,
  AppBar,
  Toolbar,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Tabs,
  Tab
} from '@mui/material';
import {
  Home as HomeIcon,
  People as PeopleIcon,
  History as HistoryIcon,
  Assessment as ReportsIcon,
  Settings as SettingsIcon,
  Save as SaveIcon,
  Backup as BackupIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
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

export default function Settings() {
  const [tabValue, setTabValue] = useState(0);
  const [settings, setSettings] = useState({
    // General settings
    companyName: 'Face Attendance System',
    workingHours: '08:00-17:00',
    timezone: 'Asia/Ho_Chi_Minh',
    language: 'vi',
    
    // Security settings
    sessionTimeout: 30,
    maxLoginAttempts: 3,
    passwordMinLength: 8,
    requireTwoFA: false,
    
    // Notification settings
    emailNotifications: true,
    smsNotifications: false,
    systemAlerts: true,
    attendanceAlerts: true,
    
    // Backup settings
    autoBackup: true,
    backupFrequency: 'daily',
    retentionDays: 30
  });
  
  const [saveMessage, setSaveMessage] = useState('');

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSave = () => {
    // Simulate save
    setSaveMessage('Cài đặt đã được lưu thành công!');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  const handleBackup = () => {
    // Simulate backup
    setSaveMessage('Đã tạo bản sao lưu thành công!');
    setTimeout(() => setSaveMessage(''), 3000);
  };

  return (
    <Box>
      {/* Navigation Bar */}
      <AppBar position="static" sx={{ mb: 3 }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            Cài đặt hệ thống
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
          <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Cài đặt hệ thống
        </Typography>

        {saveMessage && (
          <Alert severity="success" sx={{ mb: 3 }}>
            {saveMessage}
          </Alert>
        )}

        <Paper>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange}>
              <Tab label="Chung" />
              <Tab label="Bảo mật" />
              <Tab label="Thông báo" />
              <Tab label="Sao lưu" />
            </Tabs>
          </Box>

          {/* General Settings Tab */}
          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Tên công ty"
                  value={settings.companyName}
                  onChange={(e) => handleSettingChange('companyName', e.target.value)}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Giờ làm việc"
                  value={settings.workingHours}
                  onChange={(e) => handleSettingChange('workingHours', e.target.value)}
                  margin="normal"
                  helperText="Định dạng: HH:MM-HH:MM"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Múi giờ"
                  value={settings.timezone}
                  onChange={(e) => handleSettingChange('timezone', e.target.value)}
                  margin="normal"
                  select
                  SelectProps={{ native: true }}
                >
                  <option value="Asia/Ho_Chi_Minh">Việt Nam (UTC+7)</option>
                  <option value="Asia/Tokyo">Nhật Bản (UTC+9)</option>
                  <option value="UTC">UTC (UTC+0)</option>
                </TextField>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Ngôn ngữ"
                  value={settings.language}
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                  margin="normal"
                  select
                  SelectProps={{ native: true }}
                >
                  <option value="vi">Tiếng Việt</option>
                  <option value="en">English</option>
                  <option value="ja">日本語</option>
                </TextField>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Security Settings Tab */}
          <TabPanel value={tabValue} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Thời gian hết phiên (phút)"
                  type="number"
                  value={settings.sessionTimeout}
                  onChange={(e) => handleSettingChange('sessionTimeout', e.target.value)}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Số lần đăng nhập tối đa"
                  type="number"
                  value={settings.maxLoginAttempts}
                  onChange={(e) => handleSettingChange('maxLoginAttempts', e.target.value)}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Độ dài mật khẩu tối thiểu"
                  type="number"
                  value={settings.passwordMinLength}
                  onChange={(e) => handleSettingChange('passwordMinLength', e.target.value)}
                  margin="normal"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.requireTwoFA}
                      onChange={(e) => handleSettingChange('requireTwoFA', e.target.checked)}
                    />
                  }
                  label="Yêu cầu xác thực 2 bước"
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Notifications Tab */}
          <TabPanel value={tabValue} index={2}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  <NotificationsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Cài đặt thông báo
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.emailNotifications}
                      onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                    />
                  }
                  label="Thông báo qua Email"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.smsNotifications}
                      onChange={(e) => handleSettingChange('smsNotifications', e.target.checked)}
                    />
                  }
                  label="Thông báo qua SMS"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.systemAlerts}
                      onChange={(e) => handleSettingChange('systemAlerts', e.target.checked)}
                    />
                  }
                  label="Cảnh báo hệ thống"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.attendanceAlerts}
                      onChange={(e) => handleSettingChange('attendanceAlerts', e.target.checked)}
                    />
                  }
                  label="Cảnh báo chấm công"
                />
              </Grid>
            </Grid>
          </TabPanel>

          {/* Backup Settings Tab */}
          <TabPanel value={tabValue} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  <BackupIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Cài đặt sao lưu
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.autoBackup}
                      onChange={(e) => handleSettingChange('autoBackup', e.target.checked)}
                    />
                  }
                  label="Tự động sao lưu"
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Tần suất sao lưu"
                  value={settings.backupFrequency}
                  onChange={(e) => handleSettingChange('backupFrequency', e.target.value)}
                  select
                  SelectProps={{ native: true }}
                >
                  <option value="daily">Hàng ngày</option>
                  <option value="weekly">Hàng tuần</option>
                  <option value="monthly">Hàng tháng</option>
                </TextField>
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Lưu trữ (ngày)"
                  type="number"
                  value={settings.retentionDays}
                  onChange={(e) => handleSettingChange('retentionDays', e.target.value)}
                  helperText="Số ngày lưu trữ bản sao lưu"
                />
              </Grid>
              <Grid item xs={12}>
                <Button
                  variant="outlined"
                  startIcon={<BackupIcon />}
                  onClick={handleBackup}
                  sx={{ mr: 2 }}
                >
                  Tạo bản sao lưu ngay
                </Button>
              </Grid>
            </Grid>
          </TabPanel>

          <Divider />
          <Box sx={{ p: 3, textAlign: 'right' }}>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={handleSave}
              size="large"
            >
              Lưu cài đặt
            </Button>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}
