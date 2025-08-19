# 🌐 Admin Dashboard - Face Attendance System

## 📋 Tổng quan

Web Admin Dashboard cho phép quản lý nhân viên và upload ảnh thẻ trực tiếp từ giao diện web, thay vì phải sử dụng thiết bị ngoại vi.

## ✨ Tính năng chính

### 👥 Quản lý nhân viên
- ✅ **Thêm/Sửa/Xóa nhân viên** với thông tin đầy đủ
- ✅ **Upload ảnh thẻ nhân viên** trực tiếp từ web
- ✅ **AI tự động xử lý** ảnh và extract embedding
- ✅ **Quản lý nhiều ảnh** cho mỗi nhân viên
- ✅ **Tìm kiếm và lọc** theo phòng ban, trạng thái ảnh

### 🤖 AI Integration
- ✅ **Face Detection** - Phát hiện khuôn mặt trong ảnh
- ✅ **Anti-Spoofing** - Phát hiện ảnh giả, ảnh in
- ✅ **Face Embedding** - Trích xuất đặc trưng khuôn mặt 512-dim
- ✅ **Quality Check** - Kiểm tra chất lượng ảnh
- ✅ **Database Storage** - Lưu trữ an toàn trong PostgreSQL

## 🚀 Cách sử dụng

### 1. Khởi động hệ thống

**Windows:**
```bash
# Chạy script tự động
scripts\start_admin.bat
```

**Linux/Mac:**
```bash
# Chạy script tự động  
chmod +x scripts/start_admin.sh
./scripts/start_admin.sh
```

### 2. Truy cập Admin Dashboard

Mở trình duyệt và truy cập:
```
http://localhost:8000/admin
```

### 3. Thêm nhân viên mới

1. **Click "Thêm nhân viên"** trên dashboard
2. **Điền thông tin** cơ bản (Mã NV, Họ tên, Phòng ban...)
3. **Upload ảnh thẻ** trong section "Upload ảnh thẻ nhân viên"
4. **Click "Lưu"** để hoàn tất

### 4. Upload ảnh cho nhân viên có sẵn

1. **Tìm nhân viên** trong danh sách
2. **Click nút "📷"** (Quản lý ảnh)
3. **Upload ảnh mới** hoặc xóa ảnh cũ
4. **Hệ thống tự động xử lý** và lưu embedding

## 📊 Giao diện chính

### Dashboard Overview
```
┌─────────────────────────────────────────────────┐
│ 🏠 Face Attendance Admin Dashboard             │
├─────────────────────────────────────────────────┤
│ 👥 Nhân viên  │  📋 Main Panel                 │
│ 🕐 Chấm công  │  ┌─────────────────────────┐    │
│ 📱 Thiết bị   │  │ Employee Management     │    │
│ ⚙️ Cài đặt    │  │                         │    │
│               │  │ [+ Thêm NV] [🔍 Tìm]   │    │
│               │  │                         │    │
│               │  │ Employee List Table     │    │
│               │  └─────────────────────────┘    │
└─────────────────────────────────────────────────┘
```

### Employee Management
- **Danh sách nhân viên** với trạng thái ảnh
- **Tìm kiếm và lọc** theo nhiều tiêu chí
- **Thao tác nhanh** (Sửa/Ảnh/Xóa)

### Face Upload Modal
```
┌─────────────────────────────────────┐
│ Thêm/Sửa nhân viên                  │
├─────────────────────────────────────┤
│ Thông tin cơ bản:                   │
│ [Mã NV] [Họ tên] [Phòng ban]       │
│ [Chức vụ] [Email] [SĐT]            │
│                                     │
│ Upload ảnh thẻ:                     │
│ [📁 Chọn file...] [Preview]        │
│ ✅ AI Analysis Results              │
│                                     │
│ [Hủy] [💾 Lưu]                     │
└─────────────────────────────────────┘
```

## 🛡️ Xử lý ảnh an toàn

### Validation
- ✅ **File format**: JPG, PNG, WEBP
- ✅ **File size**: Tối đa 5MB
- ✅ **Face detection**: Phải có khuôn mặt rõ ràng
- ✅ **Anti-spoofing**: Không chấp nhận ảnh giả

### AI Processing Pipeline
```
📷 Upload → 🔍 Validate → 🤖 Detect Face → 🛡️ Anti-Spoof → 
📊 Extract Embedding → 💾 Save to DB → ✅ Complete
```

## 📋 Trạng thái ảnh

| Icon | Trạng thái | Mô tả |
|------|------------|--------|
| ❌ | Chưa có ảnh | Nhân viên chưa upload ảnh nào |
| ✅ | Đã có ảnh | Nhân viên có 1 ảnh trong hệ thống |
| ⚠️ | Nhiều ảnh | Nhân viên có nhiều hơn 1 ảnh |

## 🔧 Cấu hình

### Environment Variables
```bash
# Backend API URL (mặc định)
API_BASE_URL=http://localhost:8000/api/v1

# AI Processing (trong .env)
USE_REAL_AI=true
AI_MODEL_PATH=./models/
```

### Upload Settings
```javascript
// Trong admin.js
MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
```

## 📁 Cấu trúc thư mục

```
admin-dashboard/
├── index.html          # Giao diện chính
├── css/
│   └── admin.css       # Styles tùy chỉnh
├── js/
│   └── admin.js        # Logic JavaScript
└── README.md           # Hướng dẫn này
```

## 🐛 Troubleshooting

### Không kết nối được API
```bash
# Kiểm tra backend đang chạy
curl http://localhost:8000/health

# Kiểm tra CORS settings
# Backend đã cấu hình allow_origins=["*"]
```

### Upload ảnh thất bại
1. **Kiểm tra file size** < 5MB
2. **Kiểm tra format** (JPG/PNG)
3. **Kiểm tra có khuôn mặt** rõ ràng
4. **Kiểm tra AI dependencies** đã được cài đặt

### Database connection issues
```bash
# Chạy migration
cd backend
alembic upgrade head

# Kiểm tra PostgreSQL
psql -h localhost -U postgres -d face_attendance
```

## 🔒 Bảo mật

### Data Protection
- ✅ **Input validation** cho tất cả form fields
- ✅ **File type validation** chỉ chấp nhận ảnh
- ✅ **Size limits** ngăn chặn DoS
- ✅ **SQL injection protection** với ORM

### Face Data Security
- ✅ **Embedding storage** thay vì ảnh gốc
- ✅ **Database encryption** với PostgreSQL
- ✅ **Access control** qua API endpoints

## 📞 Hỗ trợ

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Debug Mode
```javascript
// Mở console browser (F12) để xem logs
console.log('🚀 Admin Dashboard initialized');
```
