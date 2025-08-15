# Flutter Kiosk App

## Mô tả
Ứng dụng Flutter chế độ kiosk cho thiết bị chấm công nhận diện khuôn mặt. Hỗ trợ auto-discovery server qua mDNS, chụp ảnh, gửi ảnh lên server, offline queue (mock), heartbeat monitoring.

## Cấu trúc chính
- `lib/main.dart`: Entry point chế độ kiosk
- `lib/config/`: Cấu hình thiết bị, mạng, API
- `lib/services/`: Service discovery, camera, API, offline queue
- `lib/screens/`: Giao diện kiosk, setup, discovery
- `lib/widgets/`: Widget camera, status, network
- `lib/utils/`: Tiện ích mạng, offline

## Chạy thử
```bash
# Cài đặt Flutter SDK
flutter pub get
flutter run
```

## Chức năng MVP
- Chế độ kiosk, chụp ảnh, gửi ảnh lên server (mock)
- Auto-discovery server qua mDNS (mock)
- Giao diện đơn giản, có thể mở rộng

## Lưu ý
- Chức năng AI, mDNS, offline queue đang mock cho MVP
- Không hardcode IP khi triển khai thực tế
- Đảm bảo kết nối WiFi local network
