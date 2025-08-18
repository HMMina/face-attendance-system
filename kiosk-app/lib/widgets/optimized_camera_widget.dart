/// Optimized Camera Widget for Landscape Layout
/// Widget camera tối ưu với giao diện ngang
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'dart:typed_data';
import '../services/enhanced_camera_service.dart';

class OptimizedCameraWidget extends StatefulWidget {
  final Function(Uint8List)? onImageCaptured;
  
  const OptimizedCameraWidget({
    super.key,
    this.onImageCaptured,
  });

  @override
  State<OptimizedCameraWidget> createState() => _OptimizedCameraWidgetState();
}

class _OptimizedCameraWidgetState extends State<OptimizedCameraWidget>
    with WidgetsBindingObserver {
  bool _isInitialized = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initializeCamera();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    super.didChangeAppLifecycleState(state);
    
    // Handle app lifecycle changes for camera
    if (state == AppLifecycleState.inactive) {
      // App is inactive, dispose camera to free resources
      EnhancedCameraService.dispose();
    } else if (state == AppLifecycleState.resumed) {
      // App is resumed, reinitialize camera
      _initializeCamera();
    }
  }

  Future<void> _initializeCamera() async {
    try {
      final success = await EnhancedCameraService.initialize();
      
      if (success) {
        // Optimize camera settings for face recognition
        await EnhancedCameraService.optimizeForFaceRecognition();
        
        if (mounted) {
          setState(() {
            _isInitialized = true;
            _errorMessage = null;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _isInitialized = false;
            _errorMessage = 'Không thể khởi động camera';
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isInitialized = false;
          _errorMessage = 'Lỗi khởi tạo camera: $e';
        });
      }
    }
  }

  Future<void> _retryInitialization() async {
    setState(() {
      _isInitialized = false;
      _errorMessage = null;
    });
    await _initializeCamera();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return _errorMessage != null 
        ? _buildErrorState(_errorMessage!)
        : _buildLoadingState();
    }

    final controller = EnhancedCameraService.controller;
    if (controller == null || !controller.value.isInitialized) {
      return _buildLoadingState();
    }

    return _buildCameraPreview(controller);
  }

  Widget _buildCameraPreview(CameraController controller) {
    // Get camera aspect ratio
    final aspectRatio = controller.value.aspectRatio;

    return Container(
      width: double.infinity,
      height: double.infinity,
      color: Colors.black,
      child: LayoutBuilder(
        builder: (context, constraints) {
          // Calculate the size to fit the container while maintaining aspect ratio
          double previewWidth = constraints.maxWidth;
          double previewHeight = constraints.maxHeight;
          
          if (aspectRatio > 1) {
            // Landscape camera
            previewHeight = previewWidth / aspectRatio;
            if (previewHeight > constraints.maxHeight) {
              previewHeight = constraints.maxHeight;
              previewWidth = previewHeight * aspectRatio;
            }
          } else {
            // Portrait camera
            previewWidth = previewHeight * aspectRatio;
            if (previewWidth > constraints.maxWidth) {
              previewWidth = constraints.maxWidth;
              previewHeight = previewWidth / aspectRatio;
            }
          }

          return Center(
            child: Stack(
              alignment: Alignment.center,
              children: [
                // Camera preview
                SizedBox(
                  width: previewWidth,
                  height: previewHeight,
                  child: CameraPreview(controller),
                ),
                
                // Face detection guide overlay
                _buildFaceGuideOverlay(),
                
                // Corner indicators
                _buildCornerIndicators(),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildFaceGuideOverlay() {
    return Container(
      width: 200,
      height: 250,
      decoration: BoxDecoration(
        border: Border.all(
          color: Colors.white.withOpacity(0.6),
          width: 2,
        ),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Stack(
        children: [
          // Corner brackets
          Positioned(
            top: 10,
            left: 10,
            child: Container(
              width: 20,
              height: 20,
              decoration: const BoxDecoration(
                border: Border(
                  top: BorderSide(color: Colors.white, width: 3),
                  left: BorderSide(color: Colors.white, width: 3),
                ),
              ),
            ),
          ),
          Positioned(
            top: 10,
            right: 10,
            child: Container(
              width: 20,
              height: 20,
              decoration: const BoxDecoration(
                border: Border(
                  top: BorderSide(color: Colors.white, width: 3),
                  right: BorderSide(color: Colors.white, width: 3),
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 10,
            left: 10,
            child: Container(
              width: 20,
              height: 20,
              decoration: const BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Colors.white, width: 3),
                  left: BorderSide(color: Colors.white, width: 3),
                ),
              ),
            ),
          ),
          Positioned(
            bottom: 10,
            right: 10,
            child: Container(
              width: 20,
              height: 20,
              decoration: const BoxDecoration(
                border: Border(
                  bottom: BorderSide(color: Colors.white, width: 3),
                  right: BorderSide(color: Colors.white, width: 3),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCornerIndicators() {
    return Positioned.fill(
      child: Container(
        margin: const EdgeInsets.all(20),
        child: Stack(
          children: [
            // Top-left
            const Positioned(
              top: 0,
              left: 0,
              child: Icon(
                Icons.crop_free,
                color: Colors.white70,
                size: 30,
              ),
            ),
            // Top-right
            const Positioned(
              top: 0,
              right: 0,
              child: Icon(
                Icons.crop_free,
                color: Colors.white70,
                size: 30,
              ),
            ),
            // Bottom-left
            const Positioned(
              bottom: 0,
              left: 0,
              child: Icon(
                Icons.crop_free,
                color: Colors.white70,
                size: 30,
              ),
            ),
            // Bottom-right
            const Positioned(
              bottom: 0,
              right: 0,
              child: Icon(
                Icons.crop_free,
                color: Colors.white70,
                size: 30,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLoadingState() {
    return Container(
      width: double.infinity,
      height: double.infinity,
      color: Colors.black,
      child: const Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(
            color: Colors.white,
            strokeWidth: 3,
          ),
          SizedBox(height: 16),
          Text(
            'Đang khởi động camera...',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Container(
      width: double.infinity,
      height: double.infinity,
      color: Colors.black,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(
            Icons.camera_alt_outlined,
            color: Colors.white54,
            size: 60,
          ),
          const SizedBox(height: 16),
          const Text(
            'Lỗi camera',
            style: TextStyle(
              color: Colors.white,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Không thể khởi động camera\n$error',
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () {
              _retryInitialization();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue,
              foregroundColor: Colors.white,
            ),
            child: const Text('Thử lại'),
          ),
        ],
      ),
    );
  }

  /// Capture image using the enhanced camera service
  Future<Uint8List?> captureImage() async {
    final imageBytes = await EnhancedCameraService.captureImage();
    
    if (imageBytes != null && widget.onImageCaptured != null) {
      widget.onImageCaptured!(imageBytes);
    }
    
    return imageBytes;
  }
}
