/// Widget hiển thị camera (mock cho MVP)
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';

typedef OnCapture = void Function(XFile image);

class CameraPreviewWidget extends StatefulWidget {
  final OnCapture? onCapture;
  const CameraPreviewWidget({super.key, this.onCapture});

  @override
  State<CameraPreviewWidget> createState() => _CameraPreviewWidgetState();
}

class _CameraPreviewWidgetState extends State<CameraPreviewWidget> {
  CameraController? _controller;
  Future<void>? _initializeControllerFuture;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    final cameras = await availableCameras();
    // Chỉ chọn camera trước (front)
    final frontCamera = cameras.firstWhere(
      (cam) => cam.lensDirection == CameraLensDirection.front,
      orElse: () => cameras[0],
    );
    _controller = CameraController(
      frontCamera,
      ResolutionPreset.medium,
    );
    _initializeControllerFuture = _controller!.initialize();
    setState(() {});
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_controller == null || _initializeControllerFuture == null) {
      return const Center(child: CircularProgressIndicator());
    }
    return FutureBuilder<void>(
      future: _initializeControllerFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.done) {
          return LayoutBuilder(
            builder: (context, constraints) {
              final isLandscape = constraints.maxWidth > constraints.maxHeight;
              double previewWidth, previewHeight;
              if (isLandscape) {
                previewHeight = constraints.maxHeight * 0.7;
                previewWidth = previewHeight * 4 / 3;
                if (previewWidth > constraints.maxWidth * 0.95) {
                  previewWidth = constraints.maxWidth * 0.95;
                  previewHeight = previewWidth * 3 / 4;
                }
              } else {
                previewWidth = constraints.maxWidth * 0.95;
                previewHeight = previewWidth * 3 / 4;
                if (previewHeight > constraints.maxHeight * 0.5) {
                  previewHeight = constraints.maxHeight * 0.5;
                  previewWidth = previewHeight * 4 / 3;
                }
              }
              return Center(
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    Container(
                      width: previewWidth,
                      height: previewHeight,
                      decoration: BoxDecoration(
                        color: Colors.black,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      clipBehavior: Clip.hardEdge,
                      child: AspectRatio(
                        aspectRatio: 4 / 3,
                        child: CameraPreview(_controller!),
                      ),
                    ),
                    Positioned(
                      right: 24,
                      child: FloatingActionButton(
                        onPressed: () async {
                          final image = await _controller!.takePicture();
                          if (widget.onCapture != null) widget.onCapture!(image);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Chụp ảnh thành công!')),
                          );
                        },
                        child: const Icon(Icons.camera_alt, color: Colors.black),
                        backgroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
              );
            },
          );
        } else {
          return const Center(child: CircularProgressIndicator());
        }
      },
    );
  }
}
