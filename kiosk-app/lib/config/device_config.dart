/// Cấu hình thiết bị kiosk
import 'dart:io';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/foundation.dart';
import 'dart:html' as html show window;

class DeviceConfig {
  // Generate unique device ID based on hardware hoặc environment
  static String deviceId = _generateDeviceId();
  static String deviceName = 'IT'; // Default name, will be updated from server
  static String? ipAddress;
  static String? serverIp;
  static String? token;
  
  // Testing configuration
  static bool isTestMode = _isTestMode();
  static String testPrefix = 'KIOSK_TEST';
  
  // Port mapping for devices
  static const int basePort = 8082;
  static const Map<String, int> devicePortMap = {
    'KIOSK001': 8082,
    'KIOSK002': 8083,
    'KIOSK003': 8084,
    'KIOSK004': 8085,
    'KIOSK005': 8086,
  };
  
  /// Get port for device ID (auto-calculate if not mapped)
  static int getPortForDevice(String deviceId) {
    // If explicitly mapped, use that
    if (devicePortMap.containsKey(deviceId)) {
      return devicePortMap[deviceId]!;
    }
    
    // Auto-calculate for KIOSK### pattern
    final match = RegExp(r'KIOSK(\d{3})').firstMatch(deviceId);
    if (match != null) {
      final number = int.parse(match.group(1)!);
      return basePort + (number - 1); // KIOSK001→8082, KIOSK002→8083, etc.
    }
    
    // Fallback: hash-based port assignment
    return basePort + (deviceId.hashCode % 100).abs();
  }
  
  /// Get suggested run command for device
  static String getRunCommand(String deviceId) {
    final port = getPortForDevice(deviceId);
    return 'flutter run -d chrome --web-port $port';
  }
  
  /// Get browser URL for device
  static String getBrowserUrl(String deviceId) {
    final port = getPortForDevice(deviceId);
    return 'http://localhost:$port?device_id=$deviceId';
  }
  
  /// Set device ID manually (useful for web)
  static void setDeviceId(String newDeviceId) {
    deviceId = newDeviceId;
    print('DeviceConfig: Device ID set to: $deviceId');
  }
  
  /// Set preset device ID for easy testing (web only)
  static void setPresetDeviceId(String presetDeviceId) {
    if (kIsWeb) {
      try {
        html.window.localStorage['PRESET_DEVICE_ID'] = presetDeviceId;
        deviceId = presetDeviceId;
        print('DeviceConfig: Preset device ID set to: $presetDeviceId');
      } catch (e) {
        print('DeviceConfig: Failed to set preset device ID: $e');
      }
    }
  }
  
  /// Quick setup for common device IDs
  static void setKiosk001() => setPresetDeviceId('KIOSK001');
  static void setKiosk002() => setPresetDeviceId('KIOSK002');
  
  /// Save device ID to localStorage (web only)
  static void saveToLocalStorage(String deviceId) {
    if (kIsWeb) {
      try {
        html.window.localStorage['KIOSK_DEVICE_ID'] = deviceId;
        print('DeviceConfig: Saved device ID to localStorage: $deviceId');
      } catch (e) {
        print('DeviceConfig: Failed to save to localStorage: $e');
      }
    }
  }
  
  /// Get device ID from localStorage (web only)
  static String? getFromLocalStorage() {
    if (kIsWeb) {
      try {
        final savedId = html.window.localStorage['KIOSK_DEVICE_ID'];
        if (savedId != null && savedId.isNotEmpty) {
          print('DeviceConfig: Retrieved device ID from localStorage: $savedId');
          return savedId;
        }
      } catch (e) {
        print('DeviceConfig: Failed to read from localStorage: $e');
      }
    }
    return null;
  }
  
  /// Generate unique device ID from hardware info hoặc environment
  static String _generateDeviceId() {
    try {
      // 1. For web, check URL parameters first (HIGHEST PRIORITY)
      if (kIsWeb) {
        final uri = Uri.parse(html.window.location.href);
        final deviceIdParam = uri.queryParameters['device_id'];
        if (deviceIdParam != null && deviceIdParam.isNotEmpty) {
          print('DeviceConfig: Using URL parameter device ID: $deviceIdParam');
          // Save to localStorage for future reference
          try {
            html.window.localStorage['KIOSK_DEVICE_ID'] = deviceIdParam;
          } catch (e) {
            print('DeviceConfig: Failed to save URL param to localStorage: $e');
          }
          return deviceIdParam;
        }
        
        // 2. For web, try localStorage for device_id (SECOND PRIORITY)
        try {
          final storedDeviceId = html.window.localStorage['KIOSK_DEVICE_ID'];
          if (storedDeviceId != null && storedDeviceId.isNotEmpty) {
            print('DeviceConfig: Using localStorage device ID: $storedDeviceId');
            return storedDeviceId;
          }
        } catch (e) {
          print('DeviceConfig: localStorage access failed: $e');
        }
        
        // 3. For web in test mode, use a fixed device ID (THIRD PRIORITY)
        if (_isTestMode()) {
          const webTestId = 'KIOSK001'; // Use the desired device ID
          print('DeviceConfig: Using web test device ID: $webTestId');
          return webTestId;
        }
        
        // Web production fallback
        const webProdId = 'KIOSK_WEB_001';
        print('DeviceConfig: Using web production device ID: $webProdId');
        return webProdId;
      }
      
      // 2. For mobile/desktop, check environment variable
      if (!kIsWeb) {
        final envDeviceId = Platform.environment['KIOSK_DEVICE_ID'];
        if (envDeviceId != null && envDeviceId.isNotEmpty) {
          print('DeviceConfig: Using environment device ID: $envDeviceId');
          return envDeviceId;
        }
      }
      
      // 3. Check test mode for mobile/desktop
      final isTest = _isTestMode();
      if (isTest) {
        final timestamp = DateTime.now().millisecondsSinceEpoch;
        final testId = 'KIOSK_TEST_${timestamp % 100000}';
        print('DeviceConfig: Generated test device ID: $testId');
        return testId;
      }
      
      // 4. Production: Generate từ timestamp + random
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final random = (timestamp % 1000).toString().padLeft(3, '0');
      final prodId = 'KIOSK_$random';
      print('DeviceConfig: Generated production device ID: $prodId');
      return prodId;
      
    } catch (e) {
      print('DeviceConfig: Error generating device ID: $e');
      // Ultimate fallback
      final fallbackId = 'KIOSK_${DateTime.now().millisecondsSinceEpoch % 10000}';
      print('DeviceConfig: Using fallback device ID: $fallbackId');
      return fallbackId;
    }
  }
  
  /// Check if in test mode
  static bool _isTestMode() {
    try {
      // Kiểm tra environment variables
      final testMode = Platform.environment['KIOSK_TEST_MODE'];
      final debugMode = Platform.environment['FLUTTER_DEBUG'];
      
      return testMode == 'true' || debugMode == 'true';
    } catch (e) {
      return false; // Default to production
    }
  }
  
  /// Get device info for debugging và registration
  static Future<Map<String, String>> getDeviceInfo() async {
    try {
      final deviceInfo = DeviceInfoPlugin();
      Map<String, String> info = {
        'device_id': deviceId,
        'device_name': deviceName,
        'is_test_mode': isTestMode.toString(),
      };
      
      if (Platform.isAndroid) {
        final androidInfo = await deviceInfo.androidInfo;
        info.addAll({
          'platform': 'Android',
          'model': androidInfo.model,
          'manufacturer': androidInfo.manufacturer,
          'android_id': androidInfo.id,
          'version': androidInfo.version.release,
        });
      } else if (Platform.isWindows) {
        final windowsInfo = await deviceInfo.windowsInfo;
        info.addAll({
          'platform': 'Windows',
          'computer_name': windowsInfo.computerName,
          'device_name': windowsInfo.deviceId,
        });
      } else if (Platform.isIOS) {
        final iosInfo = await deviceInfo.iosInfo;
        info.addAll({
          'platform': 'iOS',
          'model': iosInfo.model,
          'name': iosInfo.name,
          'identifier': iosInfo.identifierForVendor ?? 'unknown',
        });
      } else {
        info['platform'] = 'Web/Other';
      }
      
      return info;
    } catch (e) {
      print('DeviceConfig: Failed to get device info: $e');
      return {
        'device_id': deviceId,
        'device_name': deviceName,
        'platform': 'Unknown',
        'error': e.toString(),
      };
    }
  }
  
  /// Generate new test device ID
  static String generateTestDeviceId() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final testId = 'KIOSK_TEST_${timestamp % 100000}';
    setDeviceId(testId);
    return testId;
  }
  
  /// Register device với backend
  static Future<Map<String, dynamic>> registerWithBackend(String serverUrl) async {
    try {
      // This will be implemented with HTTP request to /api/v1/device-management/register
      print('DeviceConfig: TODO - Register device $deviceId with backend at $serverUrl');
      
      return {
        'success': true,
        'device_id': deviceId,
        'message': 'Registration endpoint to be implemented'
      };
    } catch (e) {
      return {
        'success': false,
        'error': e.toString()
      };
    }
  }
}
