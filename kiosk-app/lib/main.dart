/// Entry point cho Kiosk App
/// Chế độ kiosk, auto-discovery server, chụp ảnh, gửi ảnh lên server
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'screens/optimized_landscape_kiosk_screen.dart';
import 'config/device_config.dart';
import 'dart:html' as html show window;

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  // For web, FORCE check URL parameters every time
  if (kIsWeb) {
    // Always check current URL for device_id parameter
    final currentUri = Uri.parse(html.window.location.href);
    final deviceIdParam = currentUri.queryParameters['device_id'];
    
    print('main.dart: Current URL: ${html.window.location.href}');
    print('main.dart: URL parameters: ${currentUri.queryParameters}');
    
    if (deviceIdParam != null && deviceIdParam.isNotEmpty) {
      print('main.dart: ✅ Found device_id in URL: $deviceIdParam');
      DeviceConfig.setDeviceId(deviceIdParam);
      DeviceConfig.saveToLocalStorage(deviceIdParam);
    } else {
      print('main.dart: ❌ No device_id in URL, checking localStorage...');
      final savedId = DeviceConfig.getFromLocalStorage();
      if (savedId != null) {
        print('main.dart: ✅ Found device_id in localStorage: $savedId');
        DeviceConfig.setDeviceId(savedId);
      } else {
        print('main.dart: ❌ No device_id anywhere, using default: KIOSK001');
        DeviceConfig.setDeviceId('KIOSK001');
      }
    }
    
    print('main.dart: Final device_id: ${DeviceConfig.deviceId}');
  }
  
  // Set system UI for kiosk mode
  SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  
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
        fontFamily: 'Roboto',
        useMaterial3: true,
      ),
      home: const OptimizedLandscapeKioskScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
