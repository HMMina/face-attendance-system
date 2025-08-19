/// Face Registration Screen for Admin
/// Cho phép admin đăng ký khuôn mặt cho nhân viên
import 'package:flutter/material.dart';
import 'dart:typed_data';
import '../services/api_service.dart';
import '../services/enhanced_camera_service.dart';
import '../widgets/optimized_camera_widget.dart';

class FaceRegistrationScreen extends StatefulWidget {
  final String employeeId;
  final String employeeName;

  const FaceRegistrationScreen({
    super.key,
    required this.employeeId,
    required this.employeeName,
  });

  @override
  State<FaceRegistrationScreen> createState() => _FaceRegistrationScreenState();
}

class _FaceRegistrationScreenState extends State<FaceRegistrationScreen> {
  bool isProcessing = false;
  String status = 'Đặt khuôn mặt vào khung hình';
  Uint8List? capturedImageBytes;
  Map<String, dynamic>? registrationResult;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  Future<void> _initializeCamera() async {
    try {
      await EnhancedCameraService.initialize();
      setState(() {
        status = 'Camera sẵn sàng - Chụp ảnh để đăng ký khuôn mặt';
      });
    } catch (e) {
      setState(() {
        status = 'Lỗi camera: $e';
      });
    }
  }

  Future<void> _captureAndRegister() async {
    if (isProcessing) return;

    setState(() {
      isProcessing = true;
      status = 'Đang chụp ảnh...';
    });

    try {
      // Capture image
      final imageBytes = await EnhancedCameraService.captureImage();
      if (imageBytes == null) {
        setState(() {
          status = 'Không thể chụp ảnh';
          isProcessing = false;
        });
        return;
      }

      setState(() {
        capturedImageBytes = imageBytes;
        status = 'Đang đăng ký khuôn mặt...';
      });

      // Register face
      final result = await ApiService.registerFace(
        imageBytes,
        widget.employeeId,
        'admin_device',
      );

      setState(() {
        registrationResult = result;
        isProcessing = false;
        if (result['success']) {
          status = 'Đăng ký thành công!';
        } else {
          status = 'Lỗi: ${result['message']}';
        }
      });

      // Auto close after success
      if (result['success']) {
        await Future.delayed(const Duration(seconds: 3));
        if (mounted) {
          Navigator.of(context).pop(result);
        }
      }

    } catch (e) {
      setState(() {
        status = 'Lỗi: $e';
        isProcessing = false;
      });
    }
  }

  void _retryCapture() {
    setState(() {
      capturedImageBytes = null;
      registrationResult = null;
      status = 'Chụp lại ảnh để đăng ký khuôn mặt';
      isProcessing = false;
    });
  }

  @override
  void dispose() {
    EnhancedCameraService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A1A),
      appBar: AppBar(
        backgroundColor: Colors.blue[800],
        title: Text(
          'Đăng ký khuôn mặt',
          style: const TextStyle(color: Colors.white),
        ),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Employee info header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.blue[50],
                border: Border(
                  bottom: BorderSide(color: Colors.blue[200]!),
                ),
              ),
              child: Column(
                children: [
                  const Icon(
                    Icons.person_add,
                    size: 48,
                    color: Colors.blue,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    widget.employeeName,
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Mã NV: ${widget.employeeId}',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),

            Expanded(
              child: Row(
                children: [
                  // Camera area
                  Expanded(
                    flex: 2,
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        children: [
                          // Camera preview
                          Expanded(
                            child: Container(
                              decoration: BoxDecoration(
                                borderRadius: BorderRadius.circular(16),
                                border: Border.all(
                                  color: _getStatusColor(),
                                  width: 4,
                                ),
                                boxShadow: [
                                  BoxShadow(
                                    color: _getStatusColor().withOpacity(0.3),
                                    blurRadius: 15,
                                    spreadRadius: 2,
                                  ),
                                ],
                              ),
                              clipBehavior: Clip.hardEdge,
                              child: capturedImageBytes != null
                                  ? Image.memory(
                                      capturedImageBytes!,
                                      fit: BoxFit.cover,
                                    )
                                  : const OptimizedCameraWidget(),
                            ),
                          ),

                          const SizedBox(height: 20),

                          // Status
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 20,
                              vertical: 12,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.grey[800],
                              borderRadius: BorderRadius.circular(25),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                if (isProcessing)
                                  const SizedBox(
                                    width: 20,
                                    height: 20,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.orange,
                                    ),
                                  )
                                else
                                  Icon(
                                    _getStatusIcon(),
                                    color: _getStatusColor(),
                                    size: 24,
                                  ),
                                const SizedBox(width: 12),
                                Flexible(
                                  child: Text(
                                    status,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 16,
                                      fontWeight: FontWeight.w500,
                                    ),
                                    textAlign: TextAlign.center,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Control panel
                  Expanded(
                    flex: 1,
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          // Capture/Retry button
                          if (capturedImageBytes == null) ...[
                            ElevatedButton(
                              onPressed: isProcessing ? null : _captureAndRegister,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.blue[600],
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 40,
                                  vertical: 20,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    Icons.camera_alt,
                                    size: 48,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(height: 8),
                                  const Text(
                                    'Chụp ảnh\nĐăng ký',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ] else ...[
                            // Result display
                            if (registrationResult != null) ...[
                              Container(
                                padding: const EdgeInsets.all(20),
                                decoration: BoxDecoration(
                                  color: registrationResult!['success']
                                      ? Colors.green[50]
                                      : Colors.red[50],
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(
                                    color: registrationResult!['success']
                                        ? Colors.green[300]!
                                        : Colors.red[300]!,
                                  ),
                                ),
                                child: Column(
                                  children: [
                                    Icon(
                                      registrationResult!['success']
                                          ? Icons.check_circle
                                          : Icons.error,
                                      size: 48,
                                      color: registrationResult!['success']
                                          ? Colors.green[600]
                                          : Colors.red[600],
                                    ),
                                    const SizedBox(height: 12),
                                    Text(
                                      registrationResult!['message'] ?? 'Hoàn tất',
                                      style: TextStyle(
                                        fontSize: 16,
                                        fontWeight: FontWeight.bold,
                                        color: registrationResult!['success']
                                            ? Colors.green[800]
                                            : Colors.red[800],
                                      ),
                                      textAlign: TextAlign.center,
                                    ),
                                    if (registrationResult!['success']) ...[
                                      const SizedBox(height: 8),
                                      Text(
                                        'Tự động đóng sau 3 giây',
                                        style: TextStyle(
                                          fontSize: 14,
                                          color: Colors.grey[600],
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
                              ),
                              const SizedBox(height: 20),
                            ],

                            // Retry button
                            ElevatedButton(
                              onPressed: _retryCapture,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Colors.orange[600],
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 40,
                                  vertical: 20,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              child: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(
                                    Icons.refresh,
                                    size: 48,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(height: 8),
                                  const Text(
                                    'Chụp lại',
                                    style: TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],

                          const SizedBox(height: 40),

                          // Instructions
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.grey[100],
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Column(
                              children: [
                                Icon(
                                  Icons.info_outline,
                                  color: Colors.blue[600],
                                  size: 32,
                                ),
                                const SizedBox(height: 8),
                                const Text(
                                  'Hướng dẫn',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 8),
                                const Text(
                                  '• Nhìn thẳng vào camera\n'
                                  '• Giữ khuôn mặt trong khung\n'
                                  '• Đảm bảo ánh sáng đủ sáng\n'
                                  '• Không đeo khẩu trang',
                                  style: TextStyle(
                                    fontSize: 14,
                                    height: 1.5,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor() {
    if (isProcessing) return Colors.orange;
    if (registrationResult != null) {
      return registrationResult!['success'] ? Colors.green : Colors.red;
    }
    return Colors.blue;
  }

  IconData _getStatusIcon() {
    if (registrationResult != null) {
      return registrationResult!['success'] ? Icons.check_circle : Icons.error;
    }
    return Icons.face;
  }
}
