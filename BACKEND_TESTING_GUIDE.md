# Backend Testing Checklist

## 🚀 **Server Startup:**
```bash
cd backend
python start_server.py
```
Server sẽ chạy tại: `http://localhost:8000`

## 📋 **Endpoints cần test:**

### **1. 🔍 Health & Basic:**
```
GET  http://localhost:8000/                    # Root endpoint
GET  http://localhost:8000/health              # Health check + DB status
GET  http://localhost:8000/test                # Test endpoint
GET  http://localhost:8000/docs                # Swagger API docs
GET  http://localhost:8000/redoc               # ReDoc API docs
```

### **2. 👥 Employee Management:**
```
GET    http://localhost:8000/api/v1/employees                # List all employees
POST   http://localhost:8000/api/v1/employees                # Create employee
GET    http://localhost:8000/api/v1/employees/{id}           # Get employee by ID
PUT    http://localhost:8000/api/v1/employees/{id}           # Update employee
DELETE http://localhost:8000/api/v1/employees/{id}           # Delete employee
```

### **3. 📱 Device Management:**
```
GET    http://localhost:8000/api/v1/devices                  # List all devices
POST   http://localhost:8000/api/v1/devices                  # Register device
GET    http://localhost:8000/api/v1/devices/{id}             # Get device by ID
PUT    http://localhost:8000/api/v1/devices/{id}             # Update device
DELETE http://localhost:8000/api/v1/devices/{id}             # Delete device
```

### **4. ⏰ Attendance Management:**
```
GET    http://localhost:8000/api/v1/attendance               # List attendance records
POST   http://localhost:8000/api/v1/attendance               # Create attendance
GET    http://localhost:8000/api/v1/attendance/{id}          # Get attendance by ID
GET    http://localhost:8000/api/v1/attendance/employee/{id} # Employee attendance
```

### **5. 🔐 Authentication:**
```
POST   http://localhost:8000/api/v1/auth/login               # User login
POST   http://localhost:8000/api/v1/auth/register            # User register
GET    http://localhost:8000/api/v1/auth/me                  # Current user
```

### **6. 🌐 Network & Discovery:**
```
GET    http://localhost:8000/api/v1/network/status           # Network status
GET    http://localhost:8000/api/v1/discovery/devices        # Discover devices
POST   http://localhost:8000/api/v1/discovery/announce       # Announce service
```

### **7. 🤖 Face Recognition:**
```
POST   http://localhost:8000/api/v1/recognition/detect       # Detect faces
POST   http://localhost:8000/api/v1/recognition/identify     # Identify person
POST   http://localhost:8000/api/v1/recognition/train        # Train model
```

## 🧪 **Test Methods:**

### **A. Browser Testing:**
1. Mở trình duyệt
2. Truy cập: `http://localhost:8000/docs`
3. Test từng endpoint trong Swagger UI

### **B. Curl Testing:**
```bash
# Health check
curl http://localhost:8000/health

# Get employees
curl http://localhost:8000/api/v1/employees

# Create employee (POST with JSON)
curl -X POST http://localhost:8000/api/v1/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "email": "test@example.com"}'
```

### **C. Postman/Insomnia:**
Import Swagger JSON từ `http://localhost:8000/openapi.json`

## 🎯 **Priority Testing Order:**

### **🔥 Critical (Must Work):**
1. ✅ `GET /health` - Server health
2. ✅ `GET /docs` - API documentation
3. ✅ `GET /api/v1/employees` - Core functionality

### **⚡ Important:**
4. `POST /api/v1/employees` - CRUD operations
5. `GET /api/v1/devices` - Device management
6. `POST /api/v1/attendance` - Main feature

### **📱 Kiosk Integration:**
7. `POST /api/v1/recognition/identify` - Face recognition
8. `GET /api/v1/discovery/devices` - Device discovery
9. `POST /api/v1/attendance` - Check-in/out

## 🐛 **Expected Responses:**

### **Success Examples:**
```json
// GET /health
{
  "status": "healthy",
  "database": "connected",
  "service": "face-attendance-backend"
}

// GET /api/v1/employees
{
  "employees": [...],
  "total": 5
}
```

### **Error Examples:**
```json
// 404 Not Found
{
  "detail": "Employee not found"
}

// 422 Validation Error
{
  "detail": [
    {"field": "email", "message": "Invalid email format"}
  ]
}
```

## 🚀 **Quick Start Test:**
```bash
# 1. Start server
cd backend && python start_server.py

# 2. Test in new terminal
curl http://localhost:8000/health

# 3. Open browser
# http://localhost:8000/docs
```
