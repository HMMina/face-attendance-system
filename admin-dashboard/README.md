# Admin Dashboard - Face Attendance System

## Mô tả
Admin Dashboard React quản lý nhân viên, thiết bị kiosk, lịch sử chấm công, báo cáo, giám sát mạng và trạng thái thiết bị.

## Chức năng chính
- Quản lý nhân viên, phòng ban
- Quản lý thiết bị kiosk, trạng thái, logs
- Lịch sử chấm công, báo cáo
- Giám sát mạng, trạng thái kết nối
- Đăng nhập, bảo mật token

## Cấu trúc
- `src/components/`: Thành phần giao diện (employees, devices, network, attendance, dashboard)
- `src/pages/`: Trang chính (Login, Dashboard, Employees, Devices, Network, Attendance, Reports)
- `src/services/`: API, Auth, WebSocket, Utils
- `src/hooks/`: Custom hooks (useAuth, useApi, useDevices, useNetwork)

## Chạy thử
```bash
cd admin-dashboard
npm install
npm start
```

## Tích hợp API
- Kết nối backend FastAPI qua các endpoint đã triển khai
- Sử dụng token xác thực cho các request

## Lưu ý
- Mock dữ liệu cho MVP, có thể tích hợp backend thực tế
- Sử dụng MUI cho giao diện hiện đại
