/// API service gửi ảnh lên server với error handling
import 'dart:typed_data';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'discovery_service.dart';

class ApiService {
  static const Duration _timeout = Duration(seconds: 30);
  
  /// Gửi ảnh chấm công lên server
  static Future<Map<String, dynamic>> sendAttendance(
    Uint8List imageBytes, 
    String deviceId
  ) async {
    try {
      // Get server URL from discovery service
      final serverUrl = await DiscoveryService.getServerUrl();
      if (serverUrl == null) {
        return {
          'success': false,
          'error': 'Cannot find server',
          'message': 'Server discovery failed'
        };
      }

      // Prepare multipart request
      final uri = Uri.parse('$serverUrl/api/v1/attendance/check');
      final request = http.MultipartRequest('POST', uri);
      
      // Add device ID
      request.fields['device_id'] = deviceId;
      
      // Add image file
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: 'attendance_${DateTime.now().millisecondsSinceEpoch}.jpg',
        ),
      );

      // Set headers
      request.headers['Content-Type'] = 'multipart/form-data';

      // Send request with timeout
      final response = await request.send().timeout(_timeout);
      final responseData = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        final data = json.decode(responseData);
        return {
          'success': true,
          'employee_id': data['employee_id'] ?? 'N/A',
          'employee_name': data['employee_name'] ?? 'Nhân viên',
          'confidence': data['confidence'] ?? 0.0,
          'timestamp': data['timestamp'] ?? DateTime.now().toIso8601String(),
          'action_type': data['action_type'] ?? 'checkin',
          'device_id': data['device_id'] ?? deviceId,
        };
      } else {
        final errorData = json.decode(responseData);
        return {
          'success': false,
          'error': 'Server error',
          'message': errorData['detail'] ?? 'Unknown server error',
          'status_code': response.statusCode,
        };
      }
    } on SocketException {
      return {
        'success': false,
        'error': 'Network error',
        'message': 'Cannot connect to server'
      };
    } on http.ClientException {
      return {
        'success': false,
        'error': 'HTTP error',
        'message': 'Request failed'
      };
    } on FormatException {
      return {
        'success': false,
        'error': 'Parse error',
        'message': 'Invalid server response'
      };
    } catch (e) {
      return {
        'success': false,
        'error': 'Unknown error',
        'message': e.toString()
      };
    }
  }

  /// Test server connection
  static Future<bool> testConnection() async {
    try {
      final serverUrl = await DiscoveryService.getServerUrl();
      if (serverUrl == null) return false;

      final response = await http.get(
        Uri.parse('$serverUrl/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Register face for an employee
  static Future<Map<String, dynamic>> registerFace(
    Uint8List imageBytes,
    String employeeId,
    String deviceId
  ) async {
    try {
      // Get server URL from discovery service
      final serverUrl = await DiscoveryService.getServerUrl();
      if (serverUrl == null) {
        return {
          'success': false,
          'error': 'Cannot find server',
          'message': 'Server discovery failed'
        };
      }

      // Prepare multipart request
      final uri = Uri.parse('$serverUrl/api/v1/recognition/register');
      final request = http.MultipartRequest('POST', uri);
      
      // Add employee ID and device ID
      request.fields['employee_id'] = employeeId;
      request.fields['device_id'] = deviceId;
      
      // Add image file
      request.files.add(
        http.MultipartFile.fromBytes(
          'image',
          imageBytes,
          filename: 'face_registration_${DateTime.now().millisecondsSinceEpoch}.jpg',
        ),
      );

      // Set headers
      request.headers['Content-Type'] = 'multipart/form-data';

      // Send request with timeout
      final response = await request.send().timeout(_timeout);
      final responseData = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        final data = json.decode(responseData);
        return {
          'success': true,
          'message': data['message'] ?? 'Face registered successfully',
          'employee_id': data['employee_id'] ?? employeeId,
          'embedding_id': data['embedding_id'],
          'is_primary': data['is_primary'] ?? false,
        };
      } else {
        return {
          'success': false,
          'error': 'Server error',
          'message': 'HTTP ${response.statusCode}: $responseData'
        };
      }

    } catch (e) {
      return {
        'success': false,
        'error': 'Connection error',
        'message': e.toString()
      };
    }
  }

  /// Check AI service status
  static Future<Map<String, dynamic>> checkAIStatus() async {
    try {
      final serverUrl = await DiscoveryService.getServerUrl();
      if (serverUrl == null) {
        return {
          'ai_enabled': false,
          'error': 'Server not found'
        };
      }

      final response = await http.get(
        Uri.parse('$serverUrl/api/v1/recognition/status'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_timeout);

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        return {
          'ai_enabled': false,
          'error': 'Status check failed'
        };
      }
    } catch (e) {
      return {
        'ai_enabled': false,
        'error': e.toString()
      };
    }
  }
}
