/// Tiện ích offline queue cho kiosk-app
class OfflineQueue {
  static final List<Map<String, dynamic>> queue = [];

  static void add(Map<String, dynamic> data) {
    queue.add(data);
  }

  static void clear() {
    queue.clear();
  }

  static int get length => queue.length;
}
