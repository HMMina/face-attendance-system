# 📱 Face Attendance System - Kiosk App

## 📋 Tổng quan

Kiosk App là ứng dụng Flutter chạy trên thiết bị Android, được thiết kế để hoạt động như một terminal chấm công bằng nhận diện khuôn mặt. Ứng dụng hoạt động ở chế độ kiosk mode, tự động khám phá server, chụp ảnh nhân viên và gửi lên backend để xử lý nhận diện.

## 🏗️ Kiến trúc Mobile App

```
kiosk-app/
├── android/                    # Android platform code
├── ios/                       # iOS platform code (optional)
├── lib/
│   ├── main.dart              # Entry point
│   ├── config/                # App configuration
│   ├── core/                  # Core functionality
│   ├── models/                # Data models
│   │   ├── attendance.dart    # Attendance model
│   │   ├── device.dart        # Device model
│   │   └── employee.dart      # Employee model
│   ├── screens/               # UI screens
│   │   ├── kiosk_screen.dart         # Main kiosk interface
│   │   ├── setup_screen.dart         # Initial setup
│   │   ├── server_discovery_screen.dart  # Server discovery
│   │   ├── face_registration_screen.dart # Face registration
│   │   └── optimized_landscape_kiosk_screen.dart  # Optimized UI
│   ├── services/              # Business logic services
│   │   ├── api_service.dart          # Backend API communication
│   │   ├── camera_service.dart       # Camera handling
│   │   ├── discovery_service.dart    # Server discovery
│   │   ├── device_service.dart       # Device management
│   │   ├── network_service.dart      # Network utilities
│   │   ├── heartbeat_service.dart    # Keep-alive service
│   │   └── offline_queue_service.dart # Offline data queue
│   ├── widgets/               # Reusable UI components
│   └── utils/                # Utility functions
├── assets/                   # Static assets
│   ├── images/              # App images
│   ├── icons/               # App icons
│   └── sounds/              # Sound effects
├── pubspec.yaml            # Dependencies & configuration
└── README.md              # Documentation
```

## 🛠️ Tech Stack

### **1. Flutter Framework**
- **Flutter 3.x** - Google's UI toolkit for cross-platform development
- **Dart 3.0+** - Modern programming language
- **Material Design 3** - Google's design system
- **Cupertino Icons** - iOS-style icons

### **2. State Management**
- **Provider 6.1.1** - Simple state management solution
- **BLoC Pattern 8.1.3** - Business Logic Component architecture
- **flutter_bloc 8.1.3** - Flutter-specific BLoC implementation
- **Reactive Programming** - Stream-based data flow

### **3. Camera & Image Processing**
- **Camera 0.10.5+9** - Native camera access
- **Image 4.1.3** - Image processing library
- **Image Picker 1.0.7** - Platform-agnostic image selection
- **Real-time Preview** - Live camera feed

### **4. Network & API Communication**
- **HTTP 1.1.2** - HTTP client for REST API calls
- **Dio 5.4.0** - Powerful HTTP client with interceptors
- **Connectivity Plus 5.0.2** - Network connectivity detection
- **Multicast DNS 0.3.2+4** - Service discovery protocol

### **5. Local Storage & Caching**
- **Shared Preferences 2.2.2** - Key-value storage
- **Hive 2.2.3** - NoSQL database for Flutter
- **Hive Flutter 1.1.0** - Flutter integration for Hive
- **Path Provider 2.1.2** - File system paths

### **6. Device & System Integration**
- **Device Info Plus 10.1.0** - Device information
- **Permission Handler 11.1.0** - Runtime permissions
- **Wakelock Plus 1.1.4** - Keep device awake
- **Network Info Plus 5.0.1** - Network interface info

### **7. Security & Encryption**
- **Encrypt 5.0.1** - Data encryption/decryption
- **Secure Storage** - Encrypted local storage
- **Certificate Pinning** - SSL/TLS security

### **8. Development & Testing**
- **Flutter Test** - Unit và widget testing
- **Flutter Lints 3.0.1** - Code quality analysis
- **Build Runner 2.4.7** - Code generation
- **Hive Generator 2.0.1** - Model code generation

## 🎯 Core Features

### **1. Kiosk Mode Operation**
```dart
// Kiosk mode configuration
SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
SystemChrome.setPreferredOrientations([
  DeviceOrientation.landscapeLeft,
  DeviceOrientation.landscapeRight,
]);

Features:
- Fullscreen kiosk mode
- Landscape orientation lock
- System UI hiding
- Navigation gestures disabled
- Home button disabled
- Multi-tasking prevention
```

### **2. Auto Server Discovery**
```dart
// mDNS service discovery
class DiscoveryService {
  static Future<String?> discoverServer() async {
    final discovery = MulticastDns();
    await for (final ptr in discovery.lookup<PtrResourceRecord>(
      ResourceRecordQuery.ptrRecord('_face-attendance._tcp.local'),
    )) {
      // Parse service info
      return 'http://${ptr.domainName}:8000';
    }
  }
}

Features:
- Automatic server detection trên LAN
- mDNS/Bonjour service discovery
- Fallback manual configuration
- Network change handling
- Connection retry mechanism
```

### **3. Real-time Camera Processing**
```dart
// Camera service implementation
class CameraService {
  static Future<CameraController> initializeCamera() async {
    final cameras = await availableCameras();
    final frontCamera = cameras.firstWhere(
      (camera) => camera.lensDirection == CameraLensDirection.front,
    );
    
    return CameraController(
      frontCamera,
      ResolutionPreset.high,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.jpeg,
    );
  }
}

Features:
- Front camera priority cho face capture
- High resolution image capture
- Real-time preview stream
- Auto-focus và exposure control
- Image optimization
```

### **4. Face Detection & Capture**
```dart
// Face detection logic
class FaceDetectionService {
  static Future<bool> detectFace(Uint8List imageBytes) async {
    // Implement face detection logic
    // Integration với Firebase ML Kit hoặc TensorFlow Lite
    return hasFaceDetected;
  }
  
  static Future<Uint8List> optimizeImage(Uint8List imageBytes) async {
    final image = img.decodeImage(imageBytes);
    final resized = img.copyResize(image!, width: 640, height: 480);
    return Uint8List.fromList(img.encodeJpg(resized, quality: 85));
  }
}

Features:
- Real-time face detection
- Auto-capture khi detect face
- Image quality optimization
- Multiple face handling
- Anti-spoofing measures
```

### **5. Offline Queue Management**
```dart
// Offline queue service
class OfflineQueueService {
  static Future<void> queueAttendance(AttendanceRecord record) async {
    final box = await Hive.openBox<AttendanceRecord>('offline_queue');
    await box.add(record);
  }
  
  static Future<void> syncOfflineData() async {
    final box = await Hive.openBox<AttendanceRecord>('offline_queue');
    for (final record in box.values) {
      final success = await ApiService.sendAttendance(record);
      if (success) {
        await box.delete(record.key);
      }
    }
  }
}

Features:
- Local data persistence
- Automatic sync khi online
- Retry mechanism
- Data integrity protection
- Storage cleanup
```

### **6. Device Health Monitoring**
```dart
// Heartbeat service
class HeartbeatService {
  static Timer? _heartbeatTimer;
  
  static void startHeartbeat() {
    _heartbeatTimer = Timer.periodic(Duration(minutes: 5), (timer) async {
      await ApiService.sendHeartbeat({
        'device_id': await DeviceService.getDeviceId(),
        'status': 'online',
        'timestamp': DateTime.now().toIso8601String(),
        'app_version': await DeviceService.getAppVersion(),
      });
    });
  }
}

Features:
- Periodic health check
- Server connectivity monitoring
- Device status reporting
- Performance metrics
- Error reporting
```

## 📱 User Interface

### **1. Main Kiosk Screen**
```dart
// Optimized landscape kiosk screen
class OptimizedLandscapeKioskScreen extends StatefulWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Camera preview (left side)
          Expanded(
            flex: 2,
            child: CameraPreview(cameraController),
          ),
          // Information panel (right side)
          Expanded(
            flex: 1,
            child: InformationPanel(),
          ),
        ],
      ),
    );
  }
}

Features:
- Split-screen landscape layout
- Real-time camera preview
- Status indicators
- Employee feedback
- Loading animations
- Error messages
```

### **2. Server Discovery UI**
```dart
// Server discovery screen
class ServerDiscoveryScreen extends StatefulWidget {
  Features:
  - Automatic server scanning
  - Manual server entry
  - Connection testing
  - Progress indicators
  - Network status display
}
```

### **3. Setup & Configuration**
```dart
// Setup screen
class SetupScreen extends StatefulWidget {
  Features:
  - Device registration
  - Location assignment
  - Network configuration
  - Permission requests
  - Initial sync
}
```

### **4. Face Registration**
```dart
// Face registration screen
class FaceRegistrationScreen extends StatefulWidget {
  Features:
  - Employee photo capture
  - Multiple angle capture
  - Quality verification
  - Real-time feedback
  - Upload progress
}
```

## 🔧 Configuration & Settings

### **App Configuration**
```dart
// config/app_config.dart
class AppConfig {
  static const String appName = 'Face Attendance Kiosk';
  static const String version = '1.1.0+2';
  static const Duration apiTimeout = Duration(seconds: 30);
  static const Duration heartbeatInterval = Duration(minutes: 5);
  static const int maxRetryAttempts = 3;
  static const int offlineQueueLimit = 1000;
  
  // Camera settings
  static const ResolutionPreset cameraResolution = ResolutionPreset.high;
  static const bool enableAudio = false;
  static const int imageQuality = 85;
  
  // Face detection settings
  static const double faceDetectionThreshold = 0.7;
  static const int maxFacesPerImage = 1;
  static const bool enableAntiSpoofing = true;
}
```

### **Environment Configuration**
```dart
// Different configurations for environments
class Environment {
  static const String dev = 'development';
  static const String prod = 'production';
  
  static const String current = String.fromEnvironment('ENV', defaultValue: dev);
  
  static String get baseUrl {
    switch (current) {
      case prod:
        return 'https://attendance.company.com/api/v1';
      default:
        return 'http://192.168.1.100:8000/api/v1';
    }
  }
}
```

### **Device Configuration**
```dart
// Device-specific settings
class DeviceConfig {
  static Future<Map<String, dynamic>> getDeviceInfo() async {
    final deviceInfo = DeviceInfoPlugin();
    final androidInfo = await deviceInfo.androidInfo;
    
    return {
      'device_id': androidInfo.id,
      'model': androidInfo.model,
      'manufacturer': androidInfo.manufacturer,
      'version': androidInfo.version.release,
      'sdk_int': androidInfo.version.sdkInt,
    };
  }
}
```

## 🔄 Data Flow Architecture

### **1. State Management với BLoC**
```dart
// Attendance BLoC
class AttendanceBlocState extends Equatable {
  final bool isCapturing;
  final bool isProcessing;
  final String? employeeName;
  final String? status;
  final String? errorMessage;
}

class AttendanceBloc extends Bloc<AttendanceEvent, AttendanceBlocState> {
  AttendanceBloc() : super(AttendanceBlocState.initial()) {
    on<CapturePhotoEvent>(_onCapturePhoto);
    on<ProcessAttendanceEvent>(_onProcessAttendance);
    on<ResetStateEvent>(_onResetState);
  }
  
  Future<void> _onCapturePhoto(CapturePhotoEvent event, Emitter<AttendanceBlocState> emit) async {
    emit(state.copyWith(isCapturing: true));
    
    try {
      final imageBytes = await CameraService.capturePhoto();
      add(ProcessAttendanceEvent(imageBytes));
    } catch (error) {
      emit(state.copyWith(isCapturing: false, errorMessage: error.toString()));
    }
  }
}
```

### **2. Service Layer Architecture**
```dart
// Service abstraction
abstract class AttendanceService {
  Future<AttendanceResult> processAttendance(Uint8List imageBytes);
  Future<bool> isServerAvailable();
  Future<void> syncOfflineData();
}

// Implementation
class AttendanceServiceImpl implements AttendanceService {
  final ApiService _apiService;
  final OfflineQueueService _offlineService;
  final CacheService _cacheService;
  
  @override
  Future<AttendanceResult> processAttendance(Uint8List imageBytes) async {
    // Check network connectivity
    if (await NetworkService.isConnected()) {
      return await _apiService.sendAttendance(imageBytes);
    } else {
      // Queue for offline sync
      await _offlineService.queueAttendance(imageBytes);
      return AttendanceResult.offline();
    }
  }
}
```

### **3. Repository Pattern**
```dart
// Data repository
class AttendanceRepository {
  final ApiService _apiService;
  final LocalStorageService _localStorage;
  
  Future<List<AttendanceRecord>> getAttendanceHistory() async {
    try {
      // Try to get from server first
      final serverData = await _apiService.getAttendanceHistory();
      // Cache locally
      await _localStorage.cacheAttendanceHistory(serverData);
      return serverData;
    } catch (error) {
      // Fallback to local cache
      return await _localStorage.getCachedAttendanceHistory();
    }
  }
}
```

## 🔒 Security & Privacy

### **1. Data Encryption**
```dart
// Encryption service
class EncryptionService {
  static const String _key = 'your-encryption-key';
  
  static String encryptData(String data) {
    final key = Key.fromBase64(_key);
    final iv = IV.fromSecureRandom(16);
    final encrypter = Encrypter(AES(key));
    
    return encrypter.encrypt(data, iv: iv).base64;
  }
  
  static String decryptData(String encryptedData) {
    final key = Key.fromBase64(_key);
    final encrypter = Encrypter(AES(key));
    final encrypted = Encrypted.fromBase64(encryptedData);
    
    return encrypter.decrypt(encrypted);
  }
}
```

### **2. Secure Storage**
```dart
// Secure preferences
class SecurePreferences {
  static const _storage = FlutterSecureStorage();
  
  static Future<void> setSecureString(String key, String value) async {
    await _storage.write(key: key, value: value);
  }
  
  static Future<String?> getSecureString(String key) async {
    return await _storage.read(key: key);
  }
}
```

### **3. Certificate Pinning**
```dart
// HTTP client với certificate pinning
class SecureHttpClient {
  static http.Client createSecureClient() {
    return http.Client()
      ..badCertificateCallback = (cert, host, port) {
        // Implement certificate validation
        return cert.sha1.toString() == 'expected-cert-fingerprint';
      };
  }
}
```

## 📊 Performance Optimization

### **1. Image Processing Optimization**
```dart
// Image optimization
class ImageOptimizer {
  static Future<Uint8List> optimizeForUpload(Uint8List imageBytes) async {
    return await compute(_processImage, imageBytes);
  }
  
  static Uint8List _processImage(Uint8List imageBytes) {
    final image = img.decodeImage(imageBytes)!;
    
    // Resize if too large
    final resized = image.width > 1024 || image.height > 1024
        ? img.copyResize(image, width: 1024, height: 1024)
        : image;
    
    // Compress with quality setting
    return Uint8List.fromList(img.encodeJpg(resized, quality: 85));
  }
}
```

### **2. Memory Management**
```dart
// Memory efficient camera handling
class OptimizedCameraService {
  static Timer? _memoryCleanupTimer;
  
  static void startMemoryManagement() {
    _memoryCleanupTimer = Timer.periodic(Duration(minutes: 10), (timer) {
      // Force garbage collection
      ProcessInfo.currentRss; // Trigger memory check
      
      // Clear image cache if needed
      if (ProcessInfo.currentRss > 200 * 1024 * 1024) { // 200MB
        ImageCache.clear();
      }
    });
  }
}
```

### **3. Battery Optimization**
```dart
// Battery efficient operations
class BatteryOptimizer {
  static void optimizeForBattery() {
    // Reduce camera frame rate when idle
    cameraController.setDescription(
      cameraController.description.copyWith(
        maxVideoDuration: Duration(seconds: 30),
      ),
    );
    
    // Dim screen when not in use
    Timer(Duration(minutes: 5), () {
      SystemChrome.setBrightness(0.3);
    });
  }
}
```

## 🔧 Build & Deployment

### **Android Build Configuration**
```gradle
// android/app/build.gradle
android {
    compileSdkVersion 34
    
    defaultConfig {
        applicationId "com.company.kiosk_app"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 2
        versionName "1.1.0"
        
        // Enable multidex
        multiDexEnabled true
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### **Kiosk Mode Permissions**
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.DISABLE_KEYGUARD" />
<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />

<!-- Kiosk mode permissions -->
<uses-permission android:name="android.permission.LOCK_TASK" />
<uses-permission android:name="android.permission.MANAGE_DEVICE_POLICY_KIOSK" />

<application
    android:label="Face Attendance Kiosk"
    android:theme="@style/LaunchTheme"
    android:exported="true">
    
    <activity
        android:name=".MainActivity"
        android:exported="true"
        android:launchMode="singleTask"
        android:theme="@style/LaunchTheme"
        android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
        android:hardwareAccelerated="true"
        android:windowSoftInputMode="adjustResize">
        
        <!-- Kiosk mode intent filters -->
        <intent-filter android:priority="1000">
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.HOME" />
            <category android:name="android.intent.category.DEFAULT" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
</application>
```

### **Build Commands**
```bash
# Development build
flutter run --debug

# Release build
flutter build apk --release

# Install on device
flutter install --release

# Build for different architectures
flutter build apk --split-per-abi

# Build bundle for Play Store
flutter build appbundle --release
```

## 🧪 Testing Strategy

### **Unit Tests**
```dart
// test/services/api_service_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';

void main() {
  group('ApiService Tests', () {
    test('should send attendance successfully', () async {
      // Arrange
      final mockImageBytes = Uint8List.fromList([1, 2, 3, 4]);
      
      // Act
      final result = await ApiService.sendAttendance(mockImageBytes, 'device123');
      
      // Assert
      expect(result['success'], true);
    });
    
    test('should handle network errors', () async {
      // Test network error handling
    });
  });
}
```

### **Widget Tests**
```dart
// test/screens/kiosk_screen_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('Kiosk screen should display camera preview', (WidgetTester tester) async {
    // Build the widget
    await tester.pumpWidget(MaterialApp(home: KioskScreen()));
    
    // Verify camera preview is displayed
    expect(find.byType(CameraPreview), findsOneWidget);
    
    // Verify capture button is present
    expect(find.byIcon(Icons.camera), findsOneWidget);
  });
}
```

### **Integration Tests**
```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  group('End-to-end tests', () {
    testWidgets('Complete attendance flow', (WidgetTester tester) async {
      // Launch app
      await tester.pumpWidget(KioskApp());
      
      // Wait for camera initialization
      await tester.pumpAndSettle(Duration(seconds: 3));
      
      // Tap capture button
      await tester.tap(find.byIcon(Icons.camera));
      await tester.pumpAndSettle();
      
      // Verify attendance was processed
      expect(find.text('Attendance recorded'), findsOneWidget);
    });
  });
}
```

## 📱 Device Compatibility

### **Supported Devices**
```yaml
# Minimum requirements
Android:
  min_sdk: 21 (Android 5.0)
  target_sdk: 34 (Android 14)
  ram: 2GB minimum, 4GB recommended
  storage: 100MB free space
  camera: Front-facing camera required

# Optimized for
Tablets:
  - Samsung Galaxy Tab series
  - Lenovo Tab series
  - Generic Android tablets 8"+ 

Phones:
  - Google Pixel series
  - Samsung Galaxy series
  - OnePlus devices
  - Generic Android phones

# Tested devices
- Google Pixel 6 Pro (optimized)
- Samsung Galaxy Tab A8
- OnePlus 9 Pro
- Generic Android tablets
```

### **Hardware Features**
```dart
// Feature detection
class DeviceCapabilities {
  static Future<Map<String, bool>> checkCapabilities() async {
    return {
      'has_front_camera': await _hasFrontCamera(),
      'has_flash': await _hasFlash(),
      'has_auto_focus': await _hasAutoFocus(),
      'has_network': await _hasNetworkConnection(),
      'supports_kiosk_mode': await _supportsKioskMode(),
    };
  }
}
```

## 🔄 Offline Capabilities

### **Offline Queue System**
```dart
// Robust offline handling
class OfflineManager {
  static const int maxQueueSize = 1000;
  static const Duration syncInterval = Duration(minutes: 5);
  
  static Future<void> handleOfflineAttendance(AttendanceRecord record) async {
    // Store locally with timestamp
    final box = await Hive.openBox<AttendanceRecord>('offline_queue');
    
    if (box.length >= maxQueueSize) {
      // Remove oldest records
      final oldestKey = box.keys.first;
      await box.delete(oldestKey);
    }
    
    await box.add(record);
    
    // Show offline indicator
    NotificationService.showOfflineMode();
  }
  
  static Future<void> syncWhenOnline() async {
    if (await NetworkService.isConnected()) {
      final box = await Hive.openBox<AttendanceRecord>('offline_queue');
      
      for (final record in box.values.toList()) {
        try {
          final success = await ApiService.syncOfflineRecord(record);
          if (success) {
            await box.delete(record.key);
          }
        } catch (error) {
          // Keep in queue for later retry
          break;
        }
      }
      
      NotificationService.hideOfflineMode();
    }
  }
}
```

## 🎯 Future Enhancements

### **Planned Features**
- [ ] **Edge AI Processing** - On-device face recognition
- [ ] **Multi-language Support** - i18n localization
- [ ] **Voice Feedback** - Audio confirmation
- [ ] **QR Code Backup** - Alternative identification method
- [ ] **Biometric Backup** - Fingerprint integration
- [ ] **Advanced Analytics** - Usage statistics
- [ ] **Remote Management** - MDM integration
- [ ] **Video Recording** - Security footage capability

### **Technical Improvements**
- [ ] **TensorFlow Lite** - On-device ML inference
- [ ] **WebRTC** - Real-time video streaming
- [ ] **GraphQL** - Efficient data fetching
- [ ] **Firebase Integration** - Push notifications
- [ ] **Crashlytics** - Crash reporting
- [ ] **Performance Monitoring** - Real-time metrics
- [ ] **A/B Testing** - Feature flag system
- [ ] **CI/CD Pipeline** - Automated deployment

### **Hardware Integration**
- [ ] **NFC Support** - Card-based identification
- [ ] **Bluetooth Beacons** - Proximity detection
- [ ] **IoT Sensors** - Environmental monitoring
- [ ] **External Display** - Secondary screen support
- [ ] **Printer Integration** - Receipt printing
- [ ] **Scanner Integration** - Barcode/QR scanning

---

**Phát triển bởi**: Face Attendance System Team  
**Platform**: Flutter/Android  
**Phiên bản**: 1.1.0+2  
**Cập nhật lần cuối**: August 2025  
**License**: MIT
