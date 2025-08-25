/// Service quản lý thiết bị, xác thực với server
import 'package:shared_preferences/shared_preferences.dart';
import '../config/device_config.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'discovery_service_fixed.dart';

class DeviceService {
  static String? _cachedServerUrl;

  /// Get server URL from discovery service
  static Future<String> _getServerUrl() async {
    if (_cachedServerUrl != null) {
      return _cachedServerUrl!;
    }
    
    final serverUrl = await DiscoveryService.discoverServer();
    if (serverUrl != null) {
      _cachedServerUrl = serverUrl;
      return serverUrl;
    }
    
    // Fallback to localhost
    _cachedServerUrl = 'http://localhost:8000';
    return _cachedServerUrl!;
  }

  /// Đăng ký thiết bị với server
  static Future<Map<String, dynamic>?> registerDevice() async {
    try {
      final serverUrl = await _getServerUrl();
      final apiUrl = '$serverUrl/api/v1/devices';
      
      print('DeviceService: Registering device ${DeviceConfig.deviceId} to $apiUrl');
      
      final response = await http.post(
        Uri.parse('$apiUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'device_id': DeviceConfig.deviceId,
          'name': DeviceConfig.deviceName,
          'ip_address': DeviceConfig.ipAddress,
        }),
      );
      
      print('DeviceService: Register response: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print('DeviceService: Device registered successfully: $data');
        
        // Save device info
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('device_info', jsonEncode(data));
        await prefs.setString('server_url', serverUrl);
        
        return data;
      } else {
        print('DeviceService: Registration failed: ${response.body}');
        return null;
      }
    } catch (e) {
      print('DeviceService: Registration error: $e');
      return null;
    }
  }

  /// Send heartbeat to server
  static Future<bool> sendHeartbeat() async {
    try {
      final serverUrl = await _getServerUrl();
      final apiUrl = '$serverUrl/api/v1/devices';
      
      final response = await http.post(
        Uri.parse('$apiUrl/heartbeat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'device_id': DeviceConfig.deviceId,
          'timestamp': DateTime.now().toIso8601String(),
          'network_status': 'online',
        }),
      );
      
      return response.statusCode == 200;
    } catch (e) {
      print('DeviceService: Heartbeat error: $e');
      return false;
    }
  }

  /// Get device info from server
  static Future<Map<String, dynamic>?> getDeviceInfo() async {
    try {
      final serverUrl = await _getServerUrl();
      final apiUrl = '$serverUrl/api/v1/devices';
      
      final response = await http.get(
        Uri.parse('$apiUrl/${DeviceConfig.deviceId}'),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return null;
    } catch (e) {
      print('DeviceService: Get device info error: $e');
      return null;
    }
  }

  /// Get cached device info
  static Future<Map<String, dynamic>?> getCachedDeviceInfo() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final deviceInfoString = prefs.getString('device_info');
      if (deviceInfoString != null) {
        return jsonDecode(deviceInfoString);
      }
      return null;
    } catch (e) {
      print('DeviceService: Get cached device info error: $e');
      return null;
    }
  }

  /// Initialize device (sync with database)
  static Future<bool> initializeDevice() async {
    try {
      print('DeviceService: Initializing device ${DeviceConfig.deviceId}...');
      
      // First, try to get existing device info from server
      final existingDevice = await getDeviceFromServer(DeviceConfig.deviceId);
      
      if (existingDevice != null) {
        print('DeviceService: ✅ Found existing device in database');
        print('DeviceService: Device info: ${existingDevice['name']} - ${existingDevice['device_id']}');
        
        // Update local config with database info
        DeviceConfig.deviceName = existingDevice['name'] ?? DeviceConfig.deviceName;
        DeviceConfig.ipAddress = existingDevice['ip_address'] ?? DeviceConfig.ipAddress;
        
        // Update device status to online and send heartbeat
        await sendHeartbeat();
        
        print('DeviceService: ✅ Device ${DeviceConfig.deviceId} synchronized with database');
        print('DeviceService: Device represents: ${existingDevice['name']}');
        return true;
      } else {
        print('DeviceService: ⚠️ Device ${DeviceConfig.deviceId} not found in database');
        print('DeviceService: This device_id does not exist in the devices table');
        print('DeviceService: Please check your KIOSK_DEVICE_ID configuration');
        
        // For development, we can still register unknown devices
        print('DeviceService: Attempting to register as new device...');
        final deviceInfo = await registerDevice();
        if (deviceInfo != null) {
          print('DeviceService: ✅ New device registered (but this should be pre-configured)');
          return true;
        } else {
          print('DeviceService: ❌ Failed to register device');
          return false;
        }
      }
    } catch (e) {
      print('DeviceService: ❌ Device initialization error: $e');
      return false;
    }
  }

  /// Get device info from server by device_id
  static Future<Map<String, dynamic>?> getDeviceFromServer(String deviceId) async {
    try {
      final serverUrl = await _getServerUrl();
      final apiUrl = '$serverUrl/api/v1/devices';
      
      // Get all devices and find the one with matching device_id
      final response = await http.get(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
      );
      
      if (response.statusCode == 200) {
        final List<dynamic> devices = jsonDecode(response.body);
        
        // Find device with matching device_id
        for (final device in devices) {
          if (device['device_id'] == deviceId) {
            print('DeviceService: Found device in database: $device');
            return Map<String, dynamic>.from(device);
          }
        }
        
        print('DeviceService: Device $deviceId not found in database');
        return null;
      } else {
        print('DeviceService: Failed to get devices list: ${response.statusCode}');
        return null;
      }
    } catch (e) {
      print('DeviceService: Error getting device from server: $e');
      return null;
    }
  }
}
