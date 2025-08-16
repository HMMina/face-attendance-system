# Admin Dashboard Testing Guide

## 🚀 **Khởi động hệ thống:**

### **1. Backend API (Port 8000):**
```bash
cd backend
python start_server.py
```
✅ Backend running: `http://localhost:8000`

### **2. Admin Dashboard (Port 3000):**
```bash
cd admin-dashboard
npm start
```
✅ Frontend running: `http://localhost:3000`

## 📱 **Các trang cần test:**

### **🏠 Dashboard - `http://localhost:3000/`**
**Chức năng:**
- [ ] Hiển thị tổng quan hệ thống
- [ ] Thống kê nhân viên, thiết bị
- [ ] Biểu đồ chấm công hôm nay
- [ ] Trạng thái kết nối backend
- [ ] Quick actions menu

**Test steps:**
1. Mở `http://localhost:3000`
2. Kiểm tra loading data từ API
3. Verify các số liệu thống kê
4. Test responsive design

---

### **👥 Employees - `http://localhost:3000/employees`**
**Chức năng:**
- [ ] **List employees** - Hiển thị danh sách nhân viên
- [ ] **Add employee** - Thêm nhân viên mới
- [ ] **Edit employee** - Sửa thông tin nhân viên  
- [ ] **Delete employee** - Xóa nhân viên
- [ ] **Search/Filter** - Tìm kiếm nhân viên
- [ ] **Upload photo** - Upload ảnh nhân viên

**Test cases:**
```javascript
// Test data
{
  "name": "Nguyễn Văn Test",
  "email": "test@company.com", 
  "position": "Developer",
  "department": "IT",
  "employee_id": "EMP001"
}
```

---

### **📱 Devices - `http://localhost:3000/devices`**
**Chức năng:**
- [ ] **List devices** - Hiển thị thiết bị kiosk
- [ ] **Add device** - Đăng ký thiết bị mới
- [ ] **Edit device** - Cập nhật thông tin thiết bị
- [ ] **Delete device** - Xóa thiết bị
- [ ] **Device status** - Trạng thái online/offline
- [ ] **Location management** - Quản lý vị trí

**Test cases:**
```javascript
// Test device
{
  "name": "Kiosk Lobby",
  "location": "Main Entrance",
  "ip_address": "192.168.1.100",
  "status": "active"
}
```

---

### **⏰ Attendance - `http://localhost:3000/attendance`**
**Chức năng:**
- [ ] **View attendance records** - Xem bản ghi chấm công
- [ ] **Filter by date** - Lọc theo ngày
- [ ] **Filter by employee** - Lọc theo nhân viên
- [ ] **Export data** - Xuất dữ liệu
- [ ] **Manual check-in/out** - Chấm công thủ công
- [ ] **Attendance summary** - Tổng hợp chấm công

**Test scenarios:**
- View today's attendance
- Filter last week records
- Export to CSV/Excel
- Add manual attendance entry

---

### **🌐 Network - `http://localhost:3000/network`**
**Chức năng:**
- [ ] **Network status** - Trạng thái mạng
- [ ] **Connected devices** - Thiết bị kết nối
- [ ] **Device discovery** - Tìm thiết bị mới
- [ ] **Connection logs** - Log kết nối
- [ ] **Network settings** - Cài đặt mạng

**Test points:**
- Check network connectivity
- Discover new kiosk devices
- View connection history
- Test device ping/heartbeat

---

### **📊 Reports - `http://localhost:3000/reports`**
**Chức năng:**
- [ ] **Daily reports** - Báo cáo hàng ngày
- [ ] **Weekly reports** - Báo cáo tuần
- [ ] **Monthly reports** - Báo cáo tháng
- [ ] **Employee reports** - Báo cáo theo nhân viên
- [ ] **Export options** - Tùy chọn xuất file
- [ ] **Charts & graphs** - Biểu đồ

**Test reports:**
- Generate daily attendance
- Employee punctuality report
- Device usage statistics
- Export to PDF/Excel

---

### **🔐 Login - `http://localhost:3000/login`**
**Chức năng:**
- [ ] **User authentication** - Xác thực người dùng
- [ ] **Remember login** - Ghi nhớ đăng nhập
- [ ] **Forgot password** - Quên mật khẩu
- [ ] **Session management** - Quản lý phiên

**Test credentials:**
```
Username: admin
Password: admin123
```

## 🧪 **Testing Checklist:**

### **🔥 Priority 1 - Core Functions:**
- [ ] Dashboard loads successfully
- [ ] Employee CRUD operations
- [ ] Device management
- [ ] Attendance viewing
- [ ] Backend API connectivity

### **⚡ Priority 2 - User Experience:**
- [ ] Navigation between pages
- [ ] Form validation
- [ ] Error handling
- [ ] Loading states
- [ ] Mobile responsiveness

### **📱 Priority 3 - Integration:**
- [ ] Real-time data updates
- [ ] Export functionality
- [ ] Search and filtering
- [ ] Date range selection
- [ ] Bulk operations

## 🐛 **Common Issues to Check:**

### **🚫 Connection Issues:**
```
Error: Cannot connect to backend
Fix: Ensure backend is running on port 8000
```

### **📊 Data Loading:**
```
Error: Failed to load employees
Fix: Check API endpoints and CORS settings
```

### **🔄 State Management:**
```
Error: Data not refreshing
Fix: Check React state updates and useEffect
```

## 🎯 **Quick Test Script:**

### **Browser Testing:**
1. Open `http://localhost:3000`
2. Navigate to each page
3. Test one CRUD operation per page
4. Check console for errors
5. Verify mobile view

### **API Integration:**
1. Open browser DevTools → Network tab
2. Navigate admin dashboard
3. Check API calls to `localhost:8000`
4. Verify response data
5. Test error handling (stop backend)

## ✅ **Success Criteria:**
- [ ] All pages load without errors
- [ ] CRUD operations work for employees & devices
- [ ] Data displays correctly from backend
- [ ] Navigation works smoothly
- [ ] Mobile responsive design
- [ ] Error messages show appropriately

## 🚀 **Testing URLs:**
```
http://localhost:3000/           # Dashboard
http://localhost:3000/employees  # Employee Management
http://localhost:3000/devices    # Device Management  
http://localhost:3000/attendance # Attendance Records
http://localhost:3000/network    # Network Status
http://localhost:3000/reports    # Reports & Analytics
http://localhost:3000/login      # Login Page
```
