/// Optimized Landscape Kiosk Screen
/// Giao diện ngang tối ưu: Camera trước bên trái, nút chụp và kết quả bên phải
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import '../widgets/optimized_camera_widget.dart';
import '../services/api_service.dart';
import '../services/discovery_service.dart';
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
  String attendanceType = 'IN'; // Thêm biến cho lựa chọn IN/OUT
  bool showNotification = false; // Trạng thái hiển thị notification
  int countdown = 5; // Đếm ngược
  Timer? _countdownTimer;
  
  // Animation controllers
  late AnimationController _captureController;
  late AnimationController _resultController;
  late AnimationController _notificationController; // Animation cho notification
  
  // Animations
  late Animation<double> _scaleAnimation;
  late Animation<Offset> _slideAnimation;
  late Animation<double> _fadeAnimation;
  late Animation<Offset> _notificationSlideAnimation; // Slide animation cho notification

  @override
  void initState() {
    super.initState();
    _initAnimations();
    _setSystemUI();
  }

  void _initAnimations() {
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

    // Notification animation
    _notificationController = AnimationController(
      duration: const Duration(milliseconds: 400),
      vsync: this,
    );

    _notificationSlideAnimation = Tween<Offset>(
      begin: const Offset(1.0, 0.0), // Từ phải
      end: Offset.zero, // Vào giữa
    ).animate(CurvedAnimation(
      parent: _notificationController,
      curve: Curves.easeOutBack,
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
    _countdownTimer?.cancel();
    _captureController.dispose();
    _resultController.dispose();
    _notificationController.dispose();
    super.dispose();
  }

  // Mock data for testing - Enable this for testing without backend
  static const bool useMockData = false; // Set to false for production
  
  Map<String, dynamic> _generateMockResult() {
    List<Map<String, String>> mockEmployees = [
      {
        'name': 'Nguyễn Văn An',
        'position': 'Nhân viên IT', 
        'department': 'Công nghệ thông tin',
        'employee_id': 'NV001'
      },
      {
        'name': 'Trần Thị Bình',
        'position': 'Kế toán',
        'department': 'Tài chính',
        'employee_id': 'NV002'
      },
      {
        'name': 'Lê Hoàng Cường',
        'position': 'Trưởng phòng',
        'department': 'Kinh doanh',
        'employee_id': 'NV003'
      },
      {
        'name': 'Phạm Thị Dung',
        'position': 'Thư ký',
        'department': 'Hành chính',
        'employee_id': 'NV004'
      },
      {
        'name': 'Võ Minh Tuấn',
        'position': 'Nhân viên Marketing',
        'department': 'Marketing',
        'employee_id': 'NV005'
      }
    ];

    // Simulate success/failure (85% success rate)
    final random = DateTime.now().millisecondsSinceEpoch;
    final isSuccess = (random % 100) < 85;
    
    if (!isSuccess) {
      return {
        'success': false,
        'message': 'Không nhận diện được khuôn mặt. Vui lòng thử lại.',
        'timestamp': DateTime.now().toIso8601String(),
      };
    }

    // Random select an employee for successful recognition
    final selectedEmployee = mockEmployees[random % mockEmployees.length];
    
    // Use selected attendance type
    final action = attendanceType.toLowerCase() == 'in' ? 'check_in' : 'check_out';
    final actionText = attendanceType == 'IN' ? 'Vào làm' : 'Tan ca';
    final now = DateTime.now();
    
    return {
      'success': true,
      'action': action,
      'action_text': actionText,
      'timestamp': now.toIso8601String(),
      'formatted_time': '${now.day.toString().padLeft(2, '0')}/${now.month.toString().padLeft(2, '0')}/${now.year} ${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:${now.second.toString().padLeft(2, '0')}',
      'confidence': 0.85 + (random % 15) / 100, // Random confidence 0.85-0.99
      'employee': selectedEmployee,
      'message': 'Chấm công $actionText thành công!'
    };
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
        _hideNotification();
      });
      return;
    }
    
    setState(() {
      capturedImageBytes = imageBytes;
      status = 'Đang xử lý nhận diện...';
    });

    // Mock data for testing or real API call
    Map<String, dynamic> response;
    if (useMockData) {
      // Simulate processing delay
      await Future.delayed(const Duration(milliseconds: 1500));
      response = _generateMockResult();
    } else {
      // Send to server for real recognition
      response = await ApiService.sendAttendance(imageBytes, DeviceConfig.deviceId);
    }
    
    setState(() {
      result = response;
      isProcessing = false;
      showNotification = true; // Hiển thị notification thay vì result panel
      countdown = 5; // Reset countdown
      status = response['success'] ? 'Chấm công thành công!' : 'Không nhận diện được';
    });

    // Show notification animation
    _notificationController.forward();

    // Start countdown timer
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      setState(() {
        countdown--;
      });
      
      if (countdown <= 0) {
        timer.cancel();
        _hideNotification();
      }
    });
  }

  void _hideNotification() {
    _notificationController.reverse().then((_) {
      setState(() {
        showNotification = false;
        status = 'Sẵn sàng chụp ảnh';
        isProcessing = false;
        result = null;
        capturedImageBytes = null;
        countdown = 5;
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
    return Stack(
      children: [
        // Main app UI
        Scaffold(
          backgroundColor: const Color(0xFF1A1A1A),
          body: SafeArea(
        child: Row(
          children: [
            // Left side - Camera preview với overlay
            Expanded(
              flex: 4, // Tăng từ 3 lên 4 để camera lớn hơn
              child: Container(
                padding: const EdgeInsets.all(20),
                child: Stack( // Thay Column bằng Stack
                  children: [
                    // Background camera full size
                    Column(
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
                        
                        // Camera preview full size
                        Expanded(
                          child: Container(
                            width: double.infinity,
                            decoration: BoxDecoration(
                              border: Border.all(
                                color: _getStatusColor(),
                                width: 6,
                              ),
                              borderRadius: BorderRadius.circular(20),
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
                        ),
                      ],
                    ),
                    
                    // Overlay status indicator
                    Positioned(
                      bottom: 80,
                      left: 20,
                      right: 20,
                      child: Center(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 16,
                          ),
                          decoration: BoxDecoration(
                            color: isProcessing 
                                ? Colors.black.withOpacity(0.8)
                                : Colors.black.withOpacity(0.3), // Mờ hơn khi sẵn sàng
                            borderRadius: BorderRadius.circular(30),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(isProcessing ? 0.5 : 0.2),
                                blurRadius: 15,
                                offset: const Offset(0, 5),
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
                                style: TextStyle(
                                  color: isProcessing ? Colors.white : Colors.white70, // Mờ hơn khi sẵn sàng
                                  fontSize: 18,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
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
                child: Stack( // Thay Column thành Stack
                  children: [
                    // Normal controls
                    Column(
                      children: [
                    const SizedBox(height: 20),
                    
                    // IN/OUT selection
                    Container(
                      margin: const EdgeInsets.symmetric(horizontal: 20),
                      decoration: BoxDecoration(
                        color: Colors.grey[800],
                        borderRadius: BorderRadius.circular(25),
                        border: Border.all(color: Colors.grey[600]!),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: GestureDetector(
                              onTap: () => setState(() => attendanceType = 'IN'),
                              child: Container(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                decoration: BoxDecoration(
                                  color: attendanceType == 'IN' 
                                      ? Colors.green[600] 
                                      : Colors.transparent,
                                  borderRadius: BorderRadius.circular(25),
                                ),
                                child: Text(
                                  'VÀO',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    color: attendanceType == 'IN' 
                                        ? Colors.white 
                                        : Colors.grey[400],
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ),
                          Expanded(
                            child: GestureDetector(
                              onTap: () => setState(() => attendanceType = 'OUT'),
                              child: Container(
                                padding: const EdgeInsets.symmetric(vertical: 12),
                                decoration: BoxDecoration(
                                  color: attendanceType == 'OUT' 
                                      ? Colors.red[600] 
                                      : Colors.transparent,
                                  borderRadius: BorderRadius.circular(25),
                                ),
                                child: Text(
                                  'RA',
                                  textAlign: TextAlign.center,
                                  style: TextStyle(
                                    color: attendanceType == 'OUT' 
                                        ? Colors.white 
                                        : Colors.grey[400],
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    
                    const Spacer(), // Đẩy nút xuống dưới
                    
                    // Capture button
                    AnimatedBuilder(
                      animation: _scaleAnimation,
                      builder: (context, child) {
                        return Transform.scale(
                          scale: _scaleAnimation.value,
                          child: GestureDetector(
                            onTap: _onCapturePressed,
                            child: Container(
                              width: 80, // Giảm từ 90 xuống 80
                              height: 80,
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
                                size: 40, // Giảm từ 50 xuống 40
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
                  ],
                ),
                
                // Overlay result panel
                if (showResult)
                  Positioned(
                    right: 10,
                    top: 10,
                    bottom: 10,
                    width: MediaQuery.of(context).size.width * 0.45, // Tăng từ panel nhỏ lên 45% màn hình
                    child: SlideTransition(
                      position: _slideAnimation,
                      child: FadeTransition(
                        opacity: _fadeAnimation,
                        child: Container(
                          margin: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                              colors: result != null && result!['success']
                                  ? [Colors.green[50]!, Colors.green[100]!]
                                  : [Colors.red[50]!, Colors.red[100]!],
                            ),
                            borderRadius: BorderRadius.circular(20),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.3),
                                blurRadius: 20,
                                offset: const Offset(0, 10),
                              ),
                            ],
                          ),
                          child: SingleChildScrollView(
                            padding: const EdgeInsets.all(20),
                            child: _buildResultPanel(),
                          ),
                        ),
                      ),
                    ),
                  ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    ),
        
        // Notification overlay
        if (showNotification)
          SlideTransition(
            position: _notificationSlideAnimation,
            child: _buildNotificationOverlay(),
          ),
      ],
    );
  }

  Widget _buildNotificationOverlay() {
    if (result == null) return const SizedBox.shrink();
    
    final isSuccess = result!['success'] ?? false;
    
    return Positioned.fill(
      child: Container(
        color: Colors.black.withOpacity(0.8),
        child: Center(
          child: Container(
            width: MediaQuery.of(context).size.width * 0.7,
            margin: const EdgeInsets.all(40),
            padding: const EdgeInsets.all(30),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.3),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                // Compact header với icon và message
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: isSuccess ? Colors.green[100] : Colors.red[100],
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        isSuccess ? Icons.check_circle : Icons.error,
                        size: 40,
                        color: isSuccess ? Colors.green[600] : Colors.red[600],
                      ),
                    ),
                    
                    const SizedBox(width: 16),
                    
                    Expanded(
                      child: Text(
                        result!['message'] ?? 'Thông báo',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: isSuccess ? Colors.green[700] : Colors.red[700],
                        ),
                      ),
                    ),
                  ],
                ),
                
                if (isSuccess && result!['employee'] != null) ...[
                  const SizedBox(height: 16),
                  
                  // Employee info compact
                  Container(
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.grey[50],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Column(
                      children: [
                        // Avatar + Name và attendance type
                        Row(
                          children: [
                            // Employee Avatar
                            FutureBuilder<String?>(
                              future: DiscoveryService.getServerUrl(),
                              builder: (context, snapshot) {
                                final serverUrl = snapshot.data ?? 'http://localhost:8000';
                                return CircleAvatar(
                                  radius: 30,
                                  backgroundColor: Colors.grey[300],
                                  backgroundImage: result!['employee']['avatar_url'] != null
                                      ? NetworkImage('$serverUrl${result!['employee']['avatar_url']}')
                                      : null,
                                  child: result!['employee']['avatar_url'] == null
                                      ? Icon(
                                          Icons.person,
                                          size: 30,
                                          color: Colors.grey[600],
                                        )
                                      : null,
                                );
                              },
                            ),
                            
                            const SizedBox(width: 12),
                            
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    result!['employee']['name'] ?? '',
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.black87,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '${result!['employee']['position']} - ${result!['employee']['department']}',
                                    style: TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey[600],
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                              decoration: BoxDecoration(
                                color: attendanceType == 'IN' ? Colors.green[600] : Colors.red[600],
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(
                                attendanceType == 'IN' ? 'VÀO' : 'RA',
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                        
                        const SizedBox(height: 12),
                        
                        // Time compact
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            border: Border.all(color: Colors.grey[300]!),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(
                                Icons.access_time,
                                size: 16,
                                color: Colors.grey[600],
                              ),
                              const SizedBox(width: 6),
                              Text(
                                result!['formatted_time'] ?? '',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[700],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                
                const SizedBox(height: 16),
                
                // Countdown compact
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.blue[50],
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: Colors.blue[200]!),
                  ),
                  child: Text(
                    'Tự động đóng sau $countdown giây',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.blue[700],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
          ),
        ),
      ),
    );
  }

  Widget _buildResultPanel() {
    final isSuccess = result != null && result!['success'];
    
    return Container(
      width: double.infinity,
      height: 450, // Tăng chiều cao để hiển thị đầy đủ thông tin
      padding: const EdgeInsets.all(16), // Giảm padding để tận dụng không gian
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
      child: SingleChildScrollView(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            // Result icon và status
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 16),
              decoration: BoxDecoration(
                color: isSuccess ? Colors.green[100] : Colors.red[100],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    isSuccess ? Icons.check_circle : Icons.error,
                    color: isSuccess ? Colors.green[600] : Colors.red[600],
                    size: 36,
                  ),
                  const SizedBox(width: 16),
                  Flexible(
                    child: Text(
                      status,
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: isSuccess ? Colors.green[800] : Colors.red[800],
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 12), // Giảm spacing
            
            // Employee info (if success)
            if (isSuccess && result != null) ...[
              // Employee name với background đẹp
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12), // Giảm padding
                margin: const EdgeInsets.only(bottom: 12), // Giảm margin
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Colors.green[300]!, Colors.green[400]!],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.green.withOpacity(0.3),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Text(
                      'Xin chào!',
                      style: TextStyle(
                        fontSize: 16,
                        color: Colors.white,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${result!['employee']?['name'] ?? 'Nhân viên'}',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
              
              // Employee details trong container rộng hơn
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12), // Giảm padding
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.green[200]!),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    _buildInfoRow('Vị trí', result!['employee']?['position'] ?? 'N/A'),
                    const SizedBox(height: 6), // Giảm spacing
                    _buildInfoRow('Phòng ban', result!['employee']?['department'] ?? 'N/A'),
                    const SizedBox(height: 6), // Giảm spacing
                    _buildInfoRow('Mã NV', result!['employee']?['employee_id'] ?? 'N/A'),
                  ],
                ),
              ),
              
              const SizedBox(height: 10), // Giảm spacing
              
              // Action type
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: result!['action'] == 'check_in' ? Colors.green[100] : Colors.orange[100],
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(
                    color: result!['action'] == 'check_in' ? Colors.green[300]! : Colors.orange[300]!,
                  ),
                ),
                child: Text(
                  '${result!['action_text'] ?? 'N/A'}',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    color: result!['action'] == 'check_in' ? Colors.green[700] : Colors.orange[700],
                  ),
                ),
              ),
              
              const SizedBox(height: 10), // Giảm spacing
              
              // Timestamp
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue[200]!),
                ),
                child: Text(
                  '${result!['formatted_time'] ?? DateTime.now().toString().substring(0, 19)}',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: Colors.blue[700],
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
            
            // Error info (if failed)
            if (!isSuccess && result != null) ...[
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  result!['message'] ?? 'Không thể nhận diện',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.red[600],
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
            
            const SizedBox(height: 12), // Giảm spacing
            
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
                  fontSize: 12,
                  color: Colors.black54,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      children: [
        SizedBox(
          width: 70,
          child: Text(
            '$label:',
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 12,
              color: Colors.black87,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ],
    );
  }
}
