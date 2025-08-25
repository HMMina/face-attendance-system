/// Cấu hình thiết bị kiosk
import 'dart:io';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:flutter/foundation.dart';
import 'dart:html' as html show window;

class DeviceConfig {
  // Generate unique device ID based on hardware hoặc environment
  static String deviceId = _generateDeviceId();
  static String deviceName = 'IT';
  static String? ipAddress;
  static String? serverIp;
  static String? token;
  
  // Testing configuration
  static bool isTestMode = _isTestMode();
  static String testPrefix = 'KIOSK_TEST';
  
  /// Set device ID manually (useful for web)
  static void setDeviceId(String newDeviceId) {
    deviceId = newDeviceId;
    print('DeviceConfig: Device ID manually set to: $deviceId');
  }
  
  /// Generate unique device ID from hardware info hoặc environment
  static String _generateDeviceId() {
    try {
      // 1. For web, check URL parameters first
      if (kIsWeb) {
        final uri = Uri.parse(html.window.location.href);
        final deviceIdParam = uri.queryParameters['device_id'];
        if (deviceIdParam != null && deviceIdParam.isNotEmpty) {
          print('DeviceConfig: Using URL parameter device ID: $deviceIdParam');
          return deviceIdParam;
        }
        
        // For web, try localStorage for device_id
        try {
          final storedDeviceId = html.window.localStorage['KIOSK_DEVICE_ID'];
          if (storedDeviceId != null && storedDeviceId.isNotEmpty) {
            print('DeviceConfig: Using localStorage device ID: $storedDeviceId');
            return storedDeviceId;
          }
        } catch (e) {
          print('DeviceConfig: localStorage access failed: $e');
        }
        
        // For web in test mode, use a fixed device ID
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
