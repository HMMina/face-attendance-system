# Face Attendance System Backend

## Mô tả
FastAPI backend cho hệ thống chấm công nhận diện khuôn mặt. Hỗ trợ quản lý thiết bị kiosk, service discovery qua mDNS, nhận diện khuôn mặt (mock), heartbeat, bảo mật token.

## Chạy thử local
```bash
# Cài đặt Python >=3.10, PostgreSQL
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Các API chính
- `POST /api/v1/devices/register`: Đăng ký thiết bị kiosk
- `GET /api/v1/devices/`: Danh sách thiết bị
- `POST /api/v1/devices/heartbeat`: Heartbeat thiết bị
- `GET /api/v1/discovery/mdns`: Lấy thông tin mDNS server
- `POST /api/v1/recognition/face`: Nhận diện khuôn mặt (mock)

## Service Discovery
- Sử dụng mDNS/Bonjour để thiết bị kiosk tự động tìm server
- Không hardcode IP, dùng service name `_attendance._tcp.local.`

