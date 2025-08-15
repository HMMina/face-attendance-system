/// Service heartbeat gửi trạng thái thiết bị về server (mock cho MVP)
class HeartbeatService {
  static Future<void> sendHeartbeat(String deviceId, String status) async {
    // Giả lập gửi heartbeat
    await Future.delayed(const Duration(milliseconds: 500));
  }
}
