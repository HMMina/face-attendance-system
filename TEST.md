Ngưỡng để nhận diện > 0.70 (RECOGNITION_THRESHOLD = 0.70)
- HIGH_CONFIDENCE_THRESHOLD = 0.80  
- VERY_HIGH_CONFIDENCE_THRESHOLD = 0.85 ngưỡng trung bình đã thử nghiệm là 0.7299

Nếu xuất hiện lỗi 
"ERROR: [Errno 10048] error while attempting to bind on address ('0.0.0.0', 8000): only one usage of each socket address (protocol/network address/port) is normally permitted"
-> Hãy kill process đang chiếm port 8000:
netstat -ano | findstr :8000

Chạy kiosk-app
cd kiosk-app; flutter run -d chrome --web-port 8083 --dart-define=DEVICE_ID=KIOSK002