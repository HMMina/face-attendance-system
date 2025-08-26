# Universal Kiosk Runner

Hệ thống tự động phân bổ port cho các thiết bị kiosk mới.

## Sử dụng cơ bản

```powershell
# Chạy device với auto port assignment
.\run_universal_kiosk.ps1 -DeviceId KIOSK001

# Chạy device với port tùy chỉnh
.\run_universal_kiosk.ps1 -DeviceId KIOSK002 -Port 8090

# Xem danh sách devices và trạng thái
.\run_universal_kiosk.ps1 -List

# Xem help
.\run_universal_kiosk.ps1 -Help
```

## Auto Port Assignment

| Device ID | Port | Mô tả |
|-----------|------|-------|
| KIOSK001 | 8082 | Device đầu tiên |
| KIOSK002 | 8083 | Device thứ hai |
| KIOSK003 | 8084 | Device thứ ba |
| KIOSK004 | 8085 | Device thứ tư |
| KIOSK### | 8081 + number | Auto calculation |

## Quick Start Files

- `run_kiosk001.bat` - Start KIOSK001 (port 8082)
- `run_kiosk002.bat` - Start KIOSK002 (port 8083)  
- `run_kiosk003.bat` - Start KIOSK003 (port 8084)
- `run_kiosk004.bat` - Start KIOSK004 (port 8085)
- `test_universal.bat` - Test script functionality

## Tính năng

✅ **Auto Port Assignment** - Tự động tính port cho device mới  
✅ **Port Conflict Detection** - Phát hiện port đang sử dụng  
✅ **Device Status Monitoring** - Hiển thị trạng thái running/stopped  
✅ **Chrome Auto Launch** - Tự động mở browser với URL đúng device  
✅ **Flutter Integration** - Tích hợp với Flutter development server  
✅ **Error Handling** - Xử lý lỗi và tìm port thay thế  

## Workflow Thêm Device Mới

1. Thêm device ở web admin
2. Chạy: `.\run_universal_kiosk.ps1 -DeviceId KIOSK005`
3. Script tự động assign port 8086
4. Chrome mở với URL: `http://localhost:8086/?device_id=KIOSK005`

## Troubleshooting

**Port đã sử dụng:**
- Script tự động tìm port thay thế
- Hiển thị thông báo port alternative

**Device không kết nối:**
- Kiểm tra backend running trên port 8001
- Kiểm tra device đã tạo trong database

**Flutter không start:**
- Chạy `flutter clean` và `flutter pub get`
- Kiểm tra Chrome browser available
