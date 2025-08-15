/// Giao diện chính chế độ kiosk
import 'package:flutter/material.dart';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import '../widgets/camera_preview.dart';
import '../services/api_service.dart';
import '../config/device_config.dart';

class KioskScreen extends StatefulWidget {
  const KioskScreen({super.key});

  @override
  State<KioskScreen> createState() => _KioskScreenState();
}

class _KioskScreenState extends State<KioskScreen> {
  String status = 'Chờ chụp ảnh';
  bool isLoading = false;
  Map<String, dynamic>? result;
  XFile? capturedImage;

  Future<void> _captureAndSend(Uint8List imageBytes) async {
    setState(() {
      isLoading = true;
      status = 'Đang xử lý...';
    });
    final res = await ApiService.sendAttendance(imageBytes, DeviceConfig.deviceId);
    setState(() {
      isLoading = false;
      status = res['success'] ? 'Chấm công thành công!' : 'Lỗi!';
      result = res;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Kiosk Chấm Công')),
      body: LayoutBuilder(
        builder: (context, constraints) {
          final isLandscape = constraints.maxWidth > constraints.maxHeight;
          final previewWidth = isLandscape ? constraints.maxWidth * 0.5 : constraints.maxWidth * 0.95;
          final previewHeight = previewWidth * 3 / 4;
          Widget cameraWidget = Container(
            width: previewWidth,
            height: previewHeight,
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(16),
            ),
            clipBehavior: Clip.hardEdge,
            child: CameraPreviewWidget(
              onCapture: (image) async {
                setState(() {
                  capturedImage = image;
                });
                final bytes = await image.readAsBytes();
                await _captureAndSend(bytes);
              },
            ),
          );

          Widget captureButton = Padding(
            padding: const EdgeInsets.all(16.0),
            child: FloatingActionButton(
              onPressed: () {}, // Nút chụp đã nằm trong CameraPreviewWidget
              child: const Icon(Icons.camera_alt, color: Colors.black),
              backgroundColor: Colors.white,
            ),
          );

          Widget resultWidget = Column(
            children: [
              if (capturedImage != null) ...[
                const SizedBox(height: 12),
                FutureBuilder<Uint8List>(
                  future: capturedImage!.readAsBytes(),
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.done && snapshot.hasData) {
                      return Container(
                        width: 120,
                        height: 120,
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.blueAccent),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        clipBehavior: Clip.hardEdge,
                        child: Image.memory(
                          snapshot.data!,
                          fit: BoxFit.cover,
                        ),
                      );
                    } else {
                      return const SizedBox(
                        width: 120,
                        height: 120,
                        child: Center(child: CircularProgressIndicator()),
                      );
                    }
                  },
                ),
              ],
              const SizedBox(height: 20),
              Text(status, style: const TextStyle(fontSize: 20)),
              if (result != null) ...[
                const SizedBox(height: 20),
                Text('Mã NV: ${result!['employee_id']}'),
                Text('Độ tin cậy: ${result!['confidence']}'),
                Text('Thời gian: ${result!['timestamp']}'),
              ]
            ],
          );

          if (isLandscape) {
            return Row(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                cameraWidget,
                Expanded(child: resultWidget),
              ],
            );
          } else {
            return Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                cameraWidget,
                resultWidget,
              ],
            );
          }
        },
      ),
    );
  }
}
