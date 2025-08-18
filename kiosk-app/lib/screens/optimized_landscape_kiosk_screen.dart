/// Optimized Landscape Kiosk Screen
/// Giao diện ngang tối ưu: Camera trước bên trái, nút chụp và kết quả bên phải
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:typed_data';
import 'dart:async';
import '../widgets/optimized_camera_widget.dart';
import '../services/api_service.dart';
import '../services/enhanced_camera_service.dart';
import '../config/device_config.dart';

class OptimizedLandscapeKioskScreen extends StatefulWidget {
  const OptimizedLandscapeKioskScreen({super.key});

  @override
  State<OptimizedLandscapeKioskScreen> createState() => _OptimizedLandscapeKioskScreenState();
}

class _OptimizedLandscapeKioskScreenState extends State<OptimizedLandscapeKioskScreen>
    with TickerProviderStateMixin {
  
  // States
  String status = 'Sẵn sàng chụp ảnh';
  bool isProcessing = false;
  bool showResult = false;
  Map<String, dynamic>? result;
  Uint8List? capturedImageBytes;
  Timer? _autoResetTimer;
  
  // Animation controllers
  late AnimationController _breathingController;
  late AnimationController _captureController;
  late AnimationController _resultController;
  
  // Animations
  late Animation<double> _breathingAnimation;
  late Animation<double> _scaleAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _initAnimations();
    _setSystemUI();
  }

  void _initAnimations() {
    // Breathing animation for camera frame
    _breathingController = AnimationController(
      duration: const Duration(seconds: 3),
      vsync: this,
    )..repeat(reverse: true);
    
    _breathingAnimation = Tween<double>(
      begin: 0.95,
      end: 1.05,
    ).animate(CurvedAnimation(
      parent: _breathingController,
      curve: Curves.easeInOut,
    ));

    // Capture button animation
    _captureController = AnimationController(
      duration: const Duration(milliseconds: 200),
      vsync: this,
    );
    
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.9,
    ).animate(CurvedAnimation(
      parent: _captureController,
      curve: Curves.easeInOut,
    ));

    // Result panel animation
    _resultController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    
    _slideAnimation = Tween<Offset>(
      begin: const Offset(1.0, 0.0),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _resultController,
      curve: Curves.elasticOut,
    ));
    
    _fadeAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _resultController,
      curve: const Interval(0.3, 1.0),
    ));
  }

  void _setSystemUI() {
    // Force landscape orientation and hide system UI
    SystemChrome.setPreferredOrientations([
      DeviceOrientation.landscapeLeft,
      DeviceOrientation.landscapeRight,
    ]);
    SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
  }

  @override
  void dispose() {
    _autoResetTimer?.cancel();
    _breathingController.dispose();
    _captureController.dispose();
    _resultController.dispose();
    super.dispose();
  }

  Future<void> _onCapturePressed() async {
    if (isProcessing) return;

    // Button press animation
    _captureController.forward().then((_) {
      _captureController.reverse();
    });

    // Haptic feedback
    HapticFeedback.mediumImpact();

    setState(() {
      isProcessing = true;
      status = 'Đang chụp ảnh...';
    });

    // Capture image from camera service
    final imageBytes = await EnhancedCameraService.captureImage();
    
    if (imageBytes == null) {
      setState(() {
        isProcessing = false;
        showResult = true;
        status = 'Lỗi chụp ảnh';
        result = {
          'success': false,
          'message': 'Không thể chụp ảnh, vui lòng thử lại'
        };
      });
      
      // Auto reset after 2 seconds on failure
      _autoResetTimer?.cancel();
      _autoResetTimer = Timer(const Duration(seconds: 2), () {
        _resetToInitialState();
      });
      return;
    }
    
    setState(() {
      capturedImageBytes = imageBytes;
      status = 'Đang xử lý nhận diện...';
    });

    // Send to server
    final response = await ApiService.sendAttendance(imageBytes, DeviceConfig.deviceId);
    
    setState(() {
      result = response;
      isProcessing = false;
      showResult = true;
      status = response['success'] ? 'Chấm công thành công!' : 'Không nhận diện được';
    });

    // Show result animation
    _resultController.forward();

    // Auto reset after 4 seconds
    _autoResetTimer?.cancel();
    _autoResetTimer = Timer(const Duration(seconds: 4), () {
      _resetToInitialState();
    });
  }

  void _resetToInitialState() {
    _autoResetTimer?.cancel();
    _resultController.reverse().then((_) {
      setState(() {
        status = 'Sẵn sàng chụp ảnh';
        isProcessing = false;
        showResult = false;
        result = null;
        capturedImageBytes = null;
      });
    });
  }

  Color _getStatusColor() {
    if (isProcessing) return Colors.orange;
    if (result != null && result!['success']) return Colors.green;
    if (result != null && !result!['success']) return Colors.red;
    return Colors.blue;
  }

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    
    return Scaffold(
      backgroundColor: const Color(0xFF1A1A1A),
      body: SafeArea(
        child: Row(
          children: [
            // Left side - Camera preview
            Expanded(
              flex: 3,
              child: Container(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    // Header
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Colors.blue[800]!, Colors.blue[600]!],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(12),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.3),
                            blurRadius: 10,
                            offset: const Offset(0, 4),
                          ),
                        ],
                      ),
                      child: Column(
                        children: [
                          const Text(
                            'CHẤM CÔNG KHUÔN MẶT',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 1.5,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Thiết bị: ${DeviceConfig.deviceId}',
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 16,
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Camera preview with frame
                    Expanded(
                      child: Center(
                        child: AnimatedBuilder(
                          animation: _breathingAnimation,
                          builder: (context, child) {
                            return Transform.scale(
                              scale: isProcessing ? 1.0 : _breathingAnimation.value,
                              child: Container(
                                width: screenSize.height * 0.6,
                                height: screenSize.height * 0.6,
                                decoration: BoxDecoration(
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: _getStatusColor(),
                                    width: 6,
                                  ),
                                  boxShadow: [
                                    BoxShadow(
                                      color: _getStatusColor().withOpacity(0.4),
                                      blurRadius: 20,
                                      spreadRadius: 5,
                                    ),
                                  ],
                                ),
                                child: ClipRRect(
                                  borderRadius: BorderRadius.circular(14),
                                  child: const OptimizedCameraWidget(),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 20),
                    
                    // Status indicator
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
                              Icons.face,
                              color: _getStatusColor(),
                              size: 24,
                            ),
                          const SizedBox(width: 12),
                          Text(
                            status,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 18,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            // Right side - Control panel and results
            Expanded(
              flex: 2,
              child: Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                    colors: [
                      const Color(0xFF2A2A2A),
                      const Color(0xFF1A1A1A),
                    ],
                  ),
                ),
                child: Column(
                  children: [
                    const SizedBox(height: 40),
                    
                    // Capture button
                    AnimatedBuilder(
                      animation: _scaleAnimation,
                      builder: (context, child) {
                        return Transform.scale(
                          scale: _scaleAnimation.value,
                          child: GestureDetector(
                            onTap: _onCapturePressed,
                            child: Container(
                              width: 120,
                              height: 120,
                              decoration: BoxDecoration(
                                gradient: RadialGradient(
                                  colors: isProcessing
                                      ? [Colors.grey[600]!, Colors.grey[800]!]
                                      : [Colors.blue[400]!, Colors.blue[700]!],
                                ),
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: isProcessing
                                        ? Colors.grey.withOpacity(0.3)
                                        : Colors.blue.withOpacity(0.4),
                                    blurRadius: 20,
                                    spreadRadius: 5,
                                  ),
                                ],
                              ),
                              child: Icon(
                                isProcessing ? Icons.hourglass_empty : Icons.camera_alt,
                                color: Colors.white,
                                size: 50,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
                    
                    const SizedBox(height: 20),
                    
                    const Text(
                      'Nhấn để chụp ảnh',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    
                    const SizedBox(height: 40),
                    
                    // Result panel
                    Expanded(
                      child: showResult
                          ? SlideTransition(
                              position: _slideAnimation,
                              child: FadeTransition(
                                opacity: _fadeAnimation,
                                child: _buildResultPanel(),
                              ),
                            )
                          : _buildInstructions(),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultPanel() {
    final isSuccess = result != null && result!['success'];
    
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: isSuccess ? Colors.green[50] : Colors.red[50],
        border: Border.all(
          color: isSuccess ? Colors.green[300]! : Colors.red[300]!,
          width: 2,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: (isSuccess ? Colors.green : Colors.red).withOpacity(0.2),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Captured image
          if (capturedImageBytes != null) ...[
            Container(
              width: 120,
              height: 120,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isSuccess ? Colors.green[400]! : Colors.red[400]!,
                  width: 3,
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              clipBehavior: Clip.hardEdge,
              child: Container(
                color: Colors.grey[300],
                child: const Icon(
                  Icons.person,
                  size: 60,
                  color: Colors.grey,
                ),
              ),
            ),
            const SizedBox(height: 20),
          ],
          
          // Result icon
          Icon(
            isSuccess ? Icons.check_circle : Icons.error,
            color: isSuccess ? Colors.green[600] : Colors.red[600],
            size: 50,
          ),
          
          const SizedBox(height: 16),
          
          // Status text
          Text(
            status,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: isSuccess ? Colors.green[800] : Colors.red[800],
            ),
            textAlign: TextAlign.center,
          ),
          
          const SizedBox(height: 16),
          
          // Employee info (if success)
          if (isSuccess && result != null) ...[
            Text(
              'Xin chào, ${result!['employee_name'] ?? 'Nhân viên'}!',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Colors.green[700],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Mã NV: ${result!['employee_id'] ?? 'N/A'}',
              style: TextStyle(
                fontSize: 16,
                color: Colors.green[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Thời gian: ${DateTime.now().toString().substring(0, 19)}',
              style: TextStyle(
                fontSize: 14,
                color: Colors.green[600],
              ),
            ),
          ],
          
          // Error info (if failed)
          if (!isSuccess && result != null) ...[
            Text(
              result!['message'] ?? 'Không thể nhận diện',
              style: TextStyle(
                fontSize: 16,
                color: Colors.red[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
          
          const SizedBox(height: 20),
          
          // Countdown indicator
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.grey[300]!),
            ),
            child: const Text(
              'Tự động quay lại sau 4 giây...',
              style: TextStyle(
                fontSize: 14,
                color: Colors.black54,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInstructions() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.grey[800],
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey[600]!),
      ),
      child: const Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.info_outline,
            color: Colors.white70,
            size: 40,
          ),
          SizedBox(height: 16),
          Text(
            'Hướng dẫn sử dụng',
            style: TextStyle(
              color: Colors.white,
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 16),
          Text(
            '1. Đặt khuôn mặt vào giữa khung hình\n\n'
            '2. Nhấn nút chụp ảnh\n\n'
            '3. Chờ kết quả xử lý\n\n'
            '4. Xem thông tin chấm công',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 16,
              height: 1.5,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
