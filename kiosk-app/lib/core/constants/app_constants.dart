/// Core constants for the application
class AppConstants {
  // App Info
  static const String appName = 'Face Attendance Kiosk';
  static const String appVersion = '2.0.0';
  
  // API Configuration
  static const String baseUrl = 'http://localhost:8000/api/v1';
  static const Duration requestTimeout = Duration(seconds: 30);
  static const Duration connectTimeout = Duration(seconds: 15);
  
  // Camera Configuration
  static const int cameraQuality = 80;
  static const double faceDetectionThreshold = 0.6;
  static const int maxRetries = 3;
  
  // UI Configuration
  static const Duration animationDuration = Duration(milliseconds: 300);
  static const Duration successDisplayDuration = Duration(seconds: 3);
  static const Duration errorDisplayDuration = Duration(seconds: 2);
  
  // Storage Keys
  static const String deviceIdKey = 'device_id';
  static const String serverUrlKey = 'server_url';
  static const String settingsKey = 'app_settings';
  
  // Network
  static const String mdnsServiceType = '_attendance._tcp';
  static const int discoveryTimeout = 10; // seconds
  
  // Face Recognition
  static const double minFaceSize = 0.2; // 20% of image
  static const double maxFaceSize = 0.8; // 80% of image
  static const int imageWidth = 640;
  static const int imageHeight = 480;
}

/// API endpoints
class ApiEndpoints {
  static const String recognition = '/recognition/face';
  static const String devices = '/devices';
  static const String attendance = '/attendance';
  static const String health = '/health';
  static const String discovery = '/discovery/mdns';
}

/// Error messages
class ErrorMessages {
  static const String networkError = 'Lỗi kết nối mạng';
  static const String serverError = 'Lỗi máy chủ';
  static const String cameraError = 'Lỗi camera';
  static const String faceNotDetected = 'Không phát hiện khuôn mặt';
  static const String multipleFaces = 'Phát hiện nhiều khuôn mặt';
  static const String recognitionFailed = 'Không nhận diện được';
  static const String deviceOffline = 'Thiết bị offline';
  static const String invalidResponse = 'Phản hồi không hợp lệ';
}

/// Success messages
class SuccessMessages {
  static const String attendanceSuccess = 'Chấm công thành công!';
  static const String deviceRegistered = 'Thiết bị đã đăng ký';
  static const String settingsSaved = 'Đã lưu cài đặt';
}

/// Colors
class AppColors {
  static const primaryBlue = 0xFF1976D2;
  static const successGreen = 0xFF4CAF50;
  static const errorRed = 0xFFD32F2F;
  static const warningOrange = 0xFFFF9800;
  static const backgroundDark = 0xFF121212;
  static const surfaceDark = 0xFF1E1E1E;
  static const onSurfaceLight = 0xFFFFFFFF;
}
