Ngưỡng để nhận diện > 0.7 vì ngưỡng trung bình đã thử nghiệm là 0.7299

Nếu xuất hiện lỗi 
"ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): only one usage of each socket address (protocol/network address/port) is normally permitted"
-> Hãy kill process đang chiếm port 8000:
netstat -ano | findstr :8000

Chạy kiosk-app
cd kiosk-app; flutter run -d chrome --web-port 8083 --dart-define=DEVICE_ID=KIOSK002