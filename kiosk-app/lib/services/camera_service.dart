/// Camera service (mock cho MVP)
import 'dart:typed_data';

class CameraService {
  /// Mock chụp ảnh trả về dữ liệu ảnh
  static Future<Uint8List> captureImage() async {
    // Giả lập ảnh (trả về mảng byte rỗng)
    await Future.delayed(const Duration(milliseconds: 500));
    return Uint8List(0);
  }
}
