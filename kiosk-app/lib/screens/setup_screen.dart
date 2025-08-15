/// Màn hình setup thiết bị kiosk
import 'package:flutter/material.dart';
import '../config/device_config.dart';

class SetupScreen extends StatelessWidget {
  const SetupScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Thiết lập thiết bị')), 
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text('ID thiết bị: ${DeviceConfig.deviceId}'),
            Text('Tên thiết bị: ${DeviceConfig.deviceName}'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {},
              child: const Text('Đăng ký thiết bị'),
            ),
          ],
        ),
      ),
    );
  }
}
