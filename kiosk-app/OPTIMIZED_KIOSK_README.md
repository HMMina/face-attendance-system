# Kiosk App - Hệ thống chấm công khuôn mặt

## Tổng quan

Kiosk App là ứng dụng Flutter được thiết kế dành cho thiết bị kiosk chấm công bằng nhận diện khuôn mặt. Ứng dụng có giao diện ngang tối ưu với camera preview bên trái và panel điều khiển bên phải.

## Tính năng chính

### 🎥 **Giao diện ngang tối ưu**
- Layout ngang (landscape) chuyên dụng cho kiosk
- Camera preview chiếm 60% màn hình bên trái
- Panel điều khiển và kết quả 40% bên phải
- Animation mượt mà và trải nghiệm người dùng tốt

### 📷 **Camera tối ưu**
- Tự động chọn camera trước (front camera) cho nhận diện khuôn mặt
- Độ phân giải cao (ResolutionPreset.high)
- Tắt âm thanh trong chế độ kiosk
- Khung hướng dẫn đặt khuôn mặt
- Góc crop tự động theo tỷ lệ camera

### 🔄 **Quy trình chụp ảnh**
1. **Chờ sẵn sàng**: Hiển thị camera preview với khung hướng dẫn
2. **Chụp ảnh**: Nhấn nút chụp lớn, có animation và haptic feedback
3. **Xử lý**: Upload ảnh lên server và nhận diện khuôn mặt
4. **Hiển thị kết quả**: Show ảnh đã chụp + thông tin nhân viên
5. **Auto reset**: Tự động quay lại giao diện chính sau 4 giây

### 🎨 **Giao diện & Animation**
- **Breathing effect**: Khung camera "thở" nhẹ khi chờ
- **Button animation**: Nút chụp có hiệu ứng scale khi nhấn
- **Slide transition**: Panel kết quả trượt vào từ phải
- **Color coding**: Màu sắc thay đổi theo trạng thái (xanh/đỏ/cam)
- **Dark theme**: Giao diện tối phù hợp với môi trường kiosk

## Cấu trúc thư mục

```
lib/
├── main.dart                                    # Entry point
├── screens/
│   ├── optimized_landscape_kiosk_screen.dart   # Màn hình chính mới
│   ├── kiosk_screen.dart                       # Màn hình cũ (legacy)
│   └── enhanced_kiosk_screen.dart              # Màn hình cũ (legacy)
├── widgets/
│   ├── optimized_camera_widget.dart            # Widget camera tối ưu
│   └── camera_preview.dart                     # Widget camera cũ
├── services/
│   ├── enhanced_camera_service.dart            # Service camera nâng cao
│   ├── api_service.dart                        # Service API
│   └── discovery_service.dart                  # Service tìm server
└── config/
    └── device_config.dart                      # Cấu hình thiết bị
```

## Tính năng nâng cao

### 🔧 **Enhanced Camera Service**
- Quản lý lifecycle camera tự động
- Handle app state changes (pause/resume)
- Optimize settings cho face recognition
- Error handling và retry logic
- Support multiple cameras và switch

### 📡 **API Integration**
- Timeout handling (30 seconds)
- Multipart upload với metadata
- Comprehensive error responses
- Retry mechanism cho network issues
- Support cho multiple image formats

### 🎯 **Kiosk Mode**
- Immersive sticky mode (ẩn system UI)
- Force landscape orientation
- Disable navigation gestures
- Auto-restart on errors
- Memory management tối ưu

## Cách sử dụng

### 1. Khởi động ứng dụng
```bash
cd kiosk-app
flutter run
```

### 2. Quy trình chấm công
1. **Đặt khuôn mặt** vào khung hướng dẫn trên camera
2. **Nhấn nút chụp** màu xanh lớn bên phải
3. **Chờ xử lý** - ứng dụng sẽ gửi ảnh lên server
4. **Xem kết quả** - thông tin nhân viên sẽ hiển thị
5. **Tự động reset** sau 4 giây

### 3. Xử lý lỗi
- **Lỗi camera**: Ứng dụng tự động retry
- **Lỗi mạng**: Hiển thị thông báo và retry
- **Lỗi nhận diện**: Hiển thị lỗi và reset

## API Endpoints

### POST `/api/v1/attendance/check`
Upload ảnh để chấm công

**Request:**
- `Content-Type: multipart/form-data`
- `image`: File ảnh (JPEG)
- `device_id`: ID thiết bị kiosk

**Response Success (200):**
```json
{
  "success": true,
  "employee_id": "EMP001",
  "employee_name": "Nguyễn Văn A",
  "confidence": 0.95,
  "timestamp": "2025-08-16T10:30:00",
  "action_type": "checkin",
  "device_id": "KIOSK001"
}
```

**Response Error (400/500):**
```json
{
  "success": false,
  "error": "Recognition failed",
  "message": "Face not detected or confidence too low"
}
```

## Cấu hình

### Device Config (`lib/config/device_config.dart`)
```dart
class DeviceConfig {
  static const String deviceId = 'KIOSK001';
  static const String serverUrl = 'http://192.168.1.100:8000';
  static const Duration cameraTimeout = Duration(seconds: 30);
  static const Duration apiTimeout = Duration(seconds: 30);
}
```

### Camera Settings
- **Resolution**: High (1280x720 hoặc cao hơn)
- **Format**: JPEG
- **Audio**: Disabled
- **Flash**: Auto/Off
- **Focus**: Auto
- **Exposure**: Auto

## Tối ưu hóa

### 🚀 **Performance**
- Sử dụng cached animations
- Dispose resources properly
- Optimize image processing
- Memory leak prevention
- Efficient state management

### 📱 **Responsive Design**
- Adaptive layout cho các kích thước màn hình
- Safe area handling
- Proper aspect ratio maintenance
- Orientation lock

### 🔒 **Security**
- No persistent storage của ảnh
- Secure API communication
- Device registration validation
- Error information sanitization

## Troubleshooting

### Camera không khởi động
1. Check camera permissions
2. Restart ứng dụng
3. Check hardware compatibility
4. Review device logs

### Không kết nối được server
1. Check network connectivity
2. Verify server URL trong config
3. Check firewall settings
4. Test API endpoints manually

### Lỗi nhận diện
1. Cải thiện lighting conditions
2. Đảm bảo khuôn mặt trong khung
3. Check server face recognition model
4. Review confidence threshold

## Phát triển

### Requirements
- Flutter SDK >=3.0.0
- Android/iOS development tools
- Camera permissions
- Network access

### Build Commands
```bash
# Development
flutter run

# Release Android
flutter build apk --release

# Release iOS
flutter build ios --release
```

### Testing
```bash
# Unit tests
flutter test

# Integration tests
flutter test integration_test/
```

## Roadmap

### 🔄 **Planned Features**
- [ ] Face recognition confidence tuning
- [ ] Multiple face detection
- [ ] Offline mode với sync
- [ ] Admin dashboard integration
- [ ] Real-time monitoring
- [ ] Analytics và reporting

### 🎯 **Improvements**
- [ ] Better error handling
- [ ] Enhanced animations
- [ ] Voice prompts
- [ ] Multi-language support
- [ ] Accessibility features
- [ ] Advanced kiosk controls
