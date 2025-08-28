cd kiosk-app; flutter run -d chrome --web-port 8083 --web-browser-flag="--app=http://localhost:8083/?device_id=KIOSK002"


## Cách 1: Sử dụng script tự động (KHUYẾN NGHỊ)
```powershell
# Chạy script PowerShell để tự động mở 2 kiosk với device IDs khác nhau
.\kiosk-app\run_kiosk_multiple.ps1

# Hoặc custom device IDs:
.\kiosk-app\run_kiosk_multiple.ps1 -Device1 "KIOSK001" -Device2 "KIOSK002"
```


## Cách 2: Chạy thủ công từng bước

### Bước 1: Chạy Flutter trên 2 ports khác nhau
```powershell
# Terminal 1 - Port 8082
Push-Location "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"
flutter run -d chrome --web-port 8082

# Terminal 2 - Port 8083  
Push-Location "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"
flutter run -d chrome --web-port 8083
```

### Bước 2: Mở browser với URL có device_id parameter
⚠️ **QUAN TRỌNG**: Phải mở URL có `?device_id=` parameter để app nhận đúng device ID
- **KIOSK001**: http://localhost:8082/?device_id=KIOSK001
- **KIOSK002**: http://localhost:8083/?device_id=KIOSK002

## Cách 3: Chạy với command line arguments (có thể không hoạt động)
```powershell
Push-Location "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"
flutter run -d chrome --web-port 8082 --dart-define=DEVICE_ID=KIOSK001 --web-browser-flag="--new-window" --web-browser-flag="--app=http://localhost:8082?device_id=KIOSK001"

Push-Location "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"
flutter run -d chrome --web-port 8083 --dart-define=DEVICE_ID=KIOSK002 --web-browser-flag="--new-window" --web-browser-flag="--app=http://localhost:8083?device_id=KIOSK002"
```

## ✅ Xác nhận hoạt động
- Mỗi tab browser sẽ hiển thị device ID khác nhau ở góc màn hình
- Backend sẽ nhận heartbeat từ 2 devices khác nhau
- Admin dashboard sẽ thấy 2 devices online riêng biệt



