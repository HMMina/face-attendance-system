/// Entry point cho Kiosk App
/// Chế độ kiosk, auto-discovery server, chụp ảnh, gửi ảnh lên server
import 'package:flutter/material.dart';
import 'config/device_config.dart';
import 'services/discovery_service.dart';
import 'services/camera_service.dart';
import 'services/api_service.dart';
import 'screens/kiosk_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const KioskApp());
}

class KioskApp extends StatelessWidget {
  const KioskApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Face Attendance Kiosk',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        brightness: Brightness.dark,
      ),
      home: const KioskScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
