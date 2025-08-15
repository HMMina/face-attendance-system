/// Enhanced Kiosk Screen optimized for Pixel 6 (411x891 dp)
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import '../widgets/camera_preview.dart';
import '../services/api_service.dart';
import '../config/device_config.dart';

class EnhancedKioskScreen extends StatefulWidget {
  const EnhancedKioskScreen({super.key});

  @override
  State<EnhancedKioskScreen> createState() => _EnhancedKioskScreenState();
}

class _EnhancedKioskScreenState extends State<EnhancedKioskScreen>
    with TickerProviderStateMixin {
  String status = 'Đặt khuôn mặt vào khung hình';
  bool isLoading = false;
  bool isSuccess = false;
  Map<String, dynamic>? result;
  XFile? capturedImage;
  late AnimationController _pulseController;
  late AnimationController _successController;
  late Animation<double> _pulseAnimation;
  late Animation<double> _successAnimation;

  @override
  void initState() {
    super.initState();
    
    // Animation controllers
    _pulseController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat();
    
    _successController = AnimationController(
      duration: const Duration(milliseconds: 500),
      vsync: this,
    );
    
    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(
      CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut),
    );
    
    _successAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _successController, curve: Curves.elasticOut),
    );
    
    // Set system UI mode for kiosk
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
    SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp]);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _successController.dispose();
    super.dispose();
  }

  Future<void> _captureAndSend(Uint8List imageBytes) async {
    setState(() {
      isLoading = true;
      status = 'Đang xử lý nhận diện...';
    });

    try {
      final res = await ApiService.sendAttendance(imageBytes, DeviceConfig.deviceId);
      setState(() {
        isLoading = false;
        isSuccess = res['success'];
        status = res['success'] ? 'Chấm công thành công!' : 'Không nhận diện được';
        result = res;
      });
      
      if (res['success']) {
        _successController.forward();
        // Haptic feedback
        HapticFeedback.lightImpact();
        // Auto reset after 3 seconds
        Future.delayed(const Duration(seconds: 3), () {
          if (mounted) {
            _resetState();
          }
        });
      } else {
        // Auto reset after 2 seconds on failure
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            _resetState();
          }
        });
      }
    } catch (e) {
      setState(() {
        isLoading = false;
        isSuccess = false;
        status = 'Lỗi kết nối mạng';
      });
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          _resetState();
        }
      });
    }
  }

  void _resetState() {
    setState(() {
      status = 'Đặt khuôn mặt vào khung hình';
      isLoading = false;
      isSuccess = false;
      result = null;
      capturedImage = null;
    });
    _successController.reset();
  }

  Color _getStatusColor() {
    if (isLoading) return Colors.orange;
    if (isSuccess) return Colors.green;
    if (result != null && !result!['success']) return Colors.red;
    return Colors.blue;
  }

  IconData _getStatusIcon() {
    if (isLoading) return Icons.hourglass_empty;
    if (isSuccess) return Icons.check_circle;
    if (result != null && !result!['success']) return Icons.error;
    return Icons.face;
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final isPixel6 = screenSize.width >= 400 && screenSize.width <= 420;
    
    // Optimized dimensions for Pixel 6
    final cameraSize = isPixel6 
        ? Size(screenSize.width * 0.85, screenSize.width * 0.85 * 1.2)
        : Size(screenSize.width * 0.8, screenSize.width * 0.8 * 1.2);

    return Scaffold(
      backgroundColor: Colors.grey[900],
      body: SafeArea(
        child: Column(
          children: [
            // Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.blue[800]!, Colors.blue[600]!],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.3),
                    blurRadius: 10,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Column(
                children: [
                  Text(
                    'CHẤM CÔNG BẰNG KHUÔN MẶT',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: isPixel6 ? 20 : 18,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Thiết bị: ${DeviceConfig.deviceId}',
                    style: TextStyle(
                      color: Colors.white70,
                      fontSize: isPixel6 ? 14 : 12,
                    ),
                  ),
                ],
              ),
            ),

            Expanded(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Camera Preview
                    Stack(
                      alignment: Alignment.center,
                      children: [
                        // Face detection frame
                        AnimatedBuilder(
                          animation: _pulseAnimation,
                          builder: (context, child) {
                            return Transform.scale(
                              scale: isLoading ? 1.0 : _pulseAnimation.value,
                              child: Container(
                                width: cameraSize.width + 20,
                                height: cameraSize.height + 20,
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: _getStatusColor(),
                                    width: 4,
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: _getStatusColor().withOpacity(0.3),
                                      blurRadius: 20,
                                      spreadRadius: 2,
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                        
                        // Camera widget
                        ClipRRect(
                          borderRadius: BorderRadius.circular(16),
                          child: SizedBox(
                            width: cameraSize.width,
                            height: cameraSize.height,
                            child: CameraPreviewWidget(
                              onCapture: (XFile image) async {
                                final bytes = await image.readAsBytes();
                                _captureAndSend(bytes);
                              },
                            ),
                          ),
                        ),

                        // Face guide overlay
                        if (!isLoading && !isSuccess)
                          Container(
                            width: cameraSize.width * 0.6,
                            height: cameraSize.height * 0.6,
                            decoration: BoxDecoration(
                              border: Border.all(
                                color: Colors.white.withOpacity(0.5),
                                width: 2,
                              ),
                              borderRadius: BorderRadius.circular(100),
                            ),
                          ),

                        // Loading indicator
                        if (isLoading)
                          Container(
                            width: 80,
                            height: 80,
                            decoration: BoxDecoration(
                              color: Colors.black.withOpacity(0.7),
                              borderRadius: BorderRadius.circular(40),
                            ),
                            child: const Center(
                              child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 3,
                              ),
                            ),
                          ),

                        // Success animation
                        if (isSuccess)
                          AnimatedBuilder(
                            animation: _successAnimation,
                            builder: (context, child) {
                              return Transform.scale(
                                scale: _successAnimation.value,
                                child: Container(
                                  width: 100,
                                  height: 100,
                                  decoration: BoxDecoration(
                                    color: Colors.green.withOpacity(0.9),
                                    borderRadius: BorderRadius.circular(50),
                                  ),
                                  child: const Icon(
                                    Icons.check_circle,
                                    color: Colors.white,
                                    size: 60,
                                  ),
                                ),
                              );
                            },
                          ),
                      ],
                    ),

                    const SizedBox(height: 40),

                    // Status display
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 24,
                        vertical: 16,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.grey[800],
                        borderRadius: BorderRadius.circular(30),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.3),
                            blurRadius: 10,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            _getStatusIcon(),
                            color: _getStatusColor(),
                            size: 24,
                          ),
                          const SizedBox(width: 12),
                          Text(
                            status,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: isPixel6 ? 16 : 14,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Employee info display
                    if (result != null && isSuccess) ...[
                      const SizedBox(height: 20),
                      Container(
                        padding: const EdgeInsets.all(16),
                        margin: const EdgeInsets.symmetric(horizontal: 20),
                        decoration: BoxDecoration(
                          color: Colors.green[50],
                          border: Border.all(color: Colors.green[300]!),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Column(
                          children: [
                            Text(
                              'Xin chào, ${result!['employee_name'] ?? 'Nhân viên'}!',
                              style: TextStyle(
                                fontSize: isPixel6 ? 18 : 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.green[800],
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Thời gian: ${DateTime.now().toString().substring(0, 19)}',
                              style: TextStyle(
                                fontSize: isPixel6 ? 14 : 12,
                                color: Colors.green[700],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),

            // Footer with instructions
            Container(
              padding: const EdgeInsets.all(16),
              child: Text(
                'Vui lòng đặt khuôn mặt vào giữa khung hình và giữ yên',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white70,
                  fontSize: isPixel6 ? 14 : 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
