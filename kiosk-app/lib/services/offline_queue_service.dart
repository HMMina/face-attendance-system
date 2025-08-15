/// Service offline queue (mock cho MVP)
class OfflineQueueService {
  static final List<Map<String, dynamic>> _queue = [];

  /// Thêm dữ liệu vào queue khi offline
  static void addToQueue(Map<String, dynamic> data) {
    _queue.add(data);
  }

  /// Đồng bộ dữ liệu khi online
  static Future<void> syncQueue() async {
    // Giả lập đồng bộ
    await Future.delayed(const Duration(seconds: 1));
    _queue.clear();
  }

  static int get queueLength => _queue.length;
}
