/// Service quản lý thiết bị, xác thực với server
import 'package:shared_preferences/shared_preferences.dart';
import '../config/device_config.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class DeviceService {
  static const String apiUrl = 'http://192.168.1.10:8000/api/v1/auth'; // Sử dụng discovery thực tế

  /// Đăng ký thiết bị với server
  static Future<bool> registerDevice() async {
    final prefs = await SharedPreferences.getInstance();
    final res = await http.post(
      Uri.parse('$apiUrl/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'device_id': DeviceConfig.deviceId,
        'name': DeviceConfig.deviceName,
        'ip_address': DeviceConfig.ipAddress,
      }),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      DeviceConfig.token = data['token'];
      await prefs.setString('device_token', data['token']);
      return true;
    }
    return false;
  }

  /// Đăng nhập thiết bị với server
  static Future<bool> loginDevice() async {
    final prefs = await SharedPreferences.getInstance();
    final res = await http.post(
      Uri.parse('$apiUrl/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'device_id': DeviceConfig.deviceId,
        'name': DeviceConfig.deviceName,
        'ip_address': DeviceConfig.ipAddress,
      }),
    );
    if (res.statusCode == 200) {
      final data = jsonDecode(res.body);
      DeviceConfig.token = data['token'];
      await prefs.setString('device_token', data['token']);
      return true;
    }
    return false;
  }

  /// Lấy token đã lưu
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('device_token');
  }
}
