# 🏢 Face Attendance System

Hệ thống chấm công bằng nhận dạng khuôn mặt sử dụng AI với kiến trúc microservices hiện đại.

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Kiosk App     │    │  Admin Dashboard│    │   Backend API   │
│   (Flutter)     │◄──►│    (React)      │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   PostgreSQL    │
                                               │    Database     │
                                               └─────────────────┘
```

## 🚀 Tính năng chính

### 📱 Kiosk App (Flutter)
- ✅ Chụp ảnh và nhận dạng khuôn mặt real-time
- ✅ Chấm công IN/OUT tự động
- ✅ Giao diện thân thiện với người dùng
- ✅ Network discovery tự động tìm server
- ✅ Hỗ trợ multi-device (KIOSK001, KIOSK002...)

### 👨‍💼 Admin Dashboard (React)
- ✅ Quản lý nhân viên và thông tin cá nhân
- ✅ Xem lịch sử chấm công với bộ lọc ngày
- ✅ Báo cáo xuất Excel với dữ liệu chi tiết
- ✅ Upload và quản lý ảnh nhân viên
- ✅ Dashboard thống kê real-time
- ✅ Timezone UTC+7 (Việt Nam)

### ⚙️ Backend API (FastAPI)
- ✅ RESTful API với FastAPI
- ✅ AI face recognition với InsightFace
- ✅ Anti-spoofing detection bảo mật
- ✅ Rolling template system học máy
- ✅ Multi-kiosk device management
- ✅ PostgreSQL database với Alembic migrations

## 🤖 AI & Machine Learning

### Công nghệ AI sử dụng:
- **Face Detection**: YOLOv11s cho phát hiện khuôn mặt
- **Anti-Spoofing**: YOLOv11s-cls phòng chống giả mạo
- **Face Recognition**: InsightFace Buffalo_L (512-dim embeddings)
- **Similarity Matching**: Cosine Similarity với threshold 0.65

### Template Learning System:
- 🧠 Rolling templates tự học và cải thiện độ chính xác
- 📊 Mỗi nhân viên có thể có tối đa 4 templates
- ⚡ Auto-update templates từ successful matches
- 🎯 Threshold-based decision making

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Backend** | FastAPI | 0.104+ |
| **Database** | PostgreSQL | 15+ |
| **AI/ML** | InsightFace, YOLOv11 | Latest |
| **Frontend** | React | 18+ |
| **Mobile** | Flutter | 3.16+ |
| **Containerization** | Docker | Latest |

## 📋 Yêu cầu hệ thống

### Backend Requirements:
```bash
Python 3.9+
PostgreSQL 15+
CUDA (optional, for GPU acceleration)
8GB RAM (minimum)
```

### AI Models:
```bash
YOLOv11s (detection): ~18MB
YOLOv11s-cls (anti-spoofing): ~10MB  
InsightFace Buffalo_L: ~330MB
```

## 🚀 Cài đặt và chạy

### 1. Clone Repository
```bash
git clone https://github.com/HMMina/face-attendance-system.git
cd face-attendance-system
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc .venv\Scripts\activate  # Windows

pip install -r requirements.txt
python start_server.py
```

### 3. Admin Dashboard Setup
```bash
cd admin-dashboard
npm install
npm start
```

### 4. Kiosk App Setup
```bash
cd kiosk-app
flutter pub get
flutter run -d chrome --web-port 8083
```

### 5. Docker Deployment (Recommended)
```bash
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 🔧 Cấu hình

### Environment Variables:
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/attendance
AI_MODELS_PATH=./data/models
RECOGNITION_THRESHOLD=0.65

# Admin Dashboard (.env)
REACT_APP_API_URL=http://localhost:8000
REACT_APP_TIMEZONE=Asia/Ho_Chi_Minh
```

## 📊 Database Schema

### Bảng chính:
- **employees**: Thông tin nhân viên
- **face_templates**: Templates khuôn mặt (rolling system)
- **attendance**: Lịch sử chấm công
- **devices**: Quản lý thiết bị kiosk

## 🔒 Bảo mật

- ✅ Anti-spoofing detection ngăn chặn ảnh giả
- ✅ Device authentication và device locks
- ✅ SQL injection protection với SQLAlchemy ORM
- ✅ Input validation và sanitization
- ✅ HTTPS support trong production

## 📈 Performance

- ⚡ Face recognition: ~500ms trên CPU
- ⚡ Database queries: <100ms với indexing
- ⚡ API response time: <1s average
- 🔄 Concurrent kiosk support: Unlimited
- 💾 Storage: ~50KB per attendance record

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests  
cd admin-dashboard
npm test

# AI model tests
python scripts/test_models.py
```

## 📁 Cấu trúc dự án

```
face-attendance-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── core/           # Core configurations
│   ├── data/               # AI models & uploads
│   └── alembic/            # Database migrations
├── admin-dashboard/         # React admin interface
│   ├── src/
│   │   ├── pages/         # Admin pages
│   │   ├── services/      # API services
│   │   └── utils/         # Utilities
└── kiosk-app/              # Flutter kiosk application
    ├── lib/
    │   ├── screens/       # UI screens
    │   ├── services/      # API services
    │   └── widgets/       # Reusable widgets
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👥 Team

- **Backend Development**: FastAPI + AI Integration
- **Frontend Development**: React + Flutter
- **AI/ML Engineering**: Face recognition optimization
- **DevOps**: Docker + PostgreSQL deployment

## 📞 Support

For support, email: minhah4504@gmail.com or create an issue on GitHub.

---

**🎯 Made with ❤️ for modern attendance management**
