/// Service kiểm tra và tự động reconnect mạng/server
import 'package:http/http.dart' as http;

class NetworkService {
  static Future<bool> checkServer(String serverIp) async {
    try {
      final res = await http.get(Uri.parse('http://$serverIp:8000/'));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
