/// Entry point cho Kiosk App
/// Chế độ kiosk, auto-discovery server, chụp ảnh, gửi ảnh lên server
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter/foundation.dart';
import 'screens/optimized_landscape_kiosk_screen.dart';
import 'config/device_config.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Set device ID for web (since environment variables don't work on web)
  if (kIsWeb) {
    // Check URL parameters for device_id
    final uri = Uri.base;
    final deviceIdParam = uri.queryParameters['device_id'];
    if (deviceIdParam != null && deviceIdParam.isNotEmpty) {
      DeviceConfig.setDeviceId(deviceIdParam);
    } else {
      // Default device ID for web testing
      DeviceConfig.setDeviceId('KIOSK001');
    }
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
