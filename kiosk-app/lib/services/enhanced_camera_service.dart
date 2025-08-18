/// Enhanced Camera Service for Optimized Kiosk
/// Service xử lý camera với tối ưu hóa cho kiosk mode
import 'package:camera/camera.dart';
import 'dart:typed_data';
import 'package:flutter/services.dart';

class EnhancedCameraService {
  static CameraController? _controller;
  static List<CameraDescription>? _cameras;
  static bool _isInitialized = false;
  static bool _isCapturing = false;

  /// Initialize camera service
  static Future<bool> initialize() async {
    try {
      _cameras = await availableCameras();
      
      if (_cameras == null || _cameras!.isEmpty) {
        print('No cameras available');
        return false;
      }

      // Prefer front camera for face recognition
      CameraDescription? frontCamera;
      CameraDescription? backCamera;
      
      for (final camera in _cameras!) {
        if (camera.lensDirection == CameraLensDirection.front) {
          frontCamera = camera;
        } else if (camera.lensDirection == CameraLensDirection.back) {
          backCamera = camera;
        }
      }

      // Use front camera if available, otherwise use back camera
      final selectedCamera = frontCamera ?? backCamera ?? _cameras!.first;

      _controller = CameraController(
        selectedCamera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );

      await _controller!.initialize();
      
      _isInitialized = true;
      return true;
    } catch (e) {
      print('Camera initialization error: $e');
      _isInitialized = false;
      return false;
    }
  }

  /// Get camera controller
  static CameraController? get controller => _controller;

  /// Check if camera is initialized
  static bool get isInitialized => _isInitialized && _controller != null;

  /// Check if currently capturing
  static bool get isCapturing => _isCapturing;

  /// Capture image
  static Future<Uint8List?> captureImage() async {
    if (!isInitialized || _isCapturing) {
      return null;
    }

    try {
      _isCapturing = true;
      
      // Add haptic feedback
      HapticFeedback.mediumImpact();
      
      final XFile image = await _controller!.takePicture();
      final Uint8List imageBytes = await image.readAsBytes();
      
      return imageBytes;
    } catch (e) {
      print('Image capture error: $e');
      return null;
    } finally {
      _isCapturing = false;
    }
  }

  /// Switch camera (front/back)
  static Future<bool> switchCamera() async {
    if (_cameras == null || _cameras!.length < 2) {
      return false;
    }

    try {
      final currentCamera = _controller?.description;
      CameraDescription? newCamera;

      for (final camera in _cameras!) {
        if (camera != currentCamera) {
          newCamera = camera;
          break;
        }
      }

      if (newCamera == null) return false;

      await _controller?.dispose();

      _controller = CameraController(
        newCamera,
        ResolutionPreset.high,
        enableAudio: false,
        imageFormatGroup: ImageFormatGroup.jpeg,
      );

      await _controller!.initialize();
      return true;
    } catch (e) {
      print('Camera switch error: $e');
      return false;
    }
  }

  /// Get camera info
  static Map<String, dynamic> getCameraInfo() {
    if (!isInitialized) {
      return {
        'available': false,
        'count': 0,
      };
    }

    return {
      'available': true,
      'count': _cameras?.length ?? 0,
      'current_camera': _controller?.description.name ?? 'Unknown',
      'lens_direction': _controller?.description.lensDirection.toString() ?? 'Unknown',
      'resolution': _controller?.value.previewSize?.toString() ?? 'Unknown',
    };
  }

  /// Dispose camera service
  static Future<void> dispose() async {
    try {
      await _controller?.dispose();
      _controller = null;
      _isInitialized = false;
      _isCapturing = false;
    } catch (e) {
      print('Camera disposal error: $e');
    }
  }

  /// Reset camera service
  static Future<bool> reset() async {
    await dispose();
    return await initialize();
  }

  /// Check camera permission
  static Future<bool> checkPermission() async {
    try {
      // This is a simplified check - in a real app you might want to use
      // permission_handler package for more detailed permission handling
      final cameras = await availableCameras();
      return cameras.isNotEmpty;
    } catch (e) {
      print('Camera permission check error: $e');
      return false;
    }
  }

  /// Get optimal resolution for face recognition
  static ResolutionPreset getOptimalResolution() {
    // For face recognition, medium to high resolution provides good balance
    // between quality and performance
    return ResolutionPreset.high;
  }

  /// Set flash mode (if supported)
  static Future<bool> setFlashMode(FlashMode mode) async {
    if (!isInitialized) return false;

    try {
      await _controller!.setFlashMode(mode);
      return true;
    } catch (e) {
      print('Flash mode setting error: $e');
      return false;
    }
  }

  /// Set focus mode (if supported)
  static Future<bool> setFocusMode(FocusMode mode) async {
    if (!isInitialized) return false;

    try {
      await _controller!.setFocusMode(mode);
      return true;
    } catch (e) {
      print('Focus mode setting error: $e');
      return false;
    }
  }

  /// Set exposure mode (if supported)
  static Future<bool> setExposureMode(ExposureMode mode) async {
    if (!isInitialized) return false;

    try {
      await _controller!.setExposureMode(mode);
      return true;
    } catch (e) {
      print('Exposure mode setting error: $e');
      return false;
    }
  }

  /// Configure camera for optimal face recognition
  static Future<void> optimizeForFaceRecognition() async {
    if (!isInitialized) return;

    try {
      // Set optimal settings for face recognition
      await setFlashMode(FlashMode.off);
      await setFocusMode(FocusMode.auto);
      await setExposureMode(ExposureMode.auto);
      
      print('Camera optimized for face recognition');
    } catch (e) {
      print('Camera optimization error: $e');
    }
  }
}
