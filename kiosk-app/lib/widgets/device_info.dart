/// Widget hiển thị thông tin thiết bị kiosk
import 'package:flutter/material.dart';
import '../config/device_config.dart';

class DeviceInfoWidget extends StatelessWidget {
  const DeviceInfoWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('ID thiết bị: ${DeviceConfig.deviceId}'),
        Text('Tên thiết bị: ${DeviceConfig.deviceName}'),
        if (DeviceConfig.ipAddress != null)
          Text('IP: ${DeviceConfig.ipAddress}'),
      ],
    );
  }
}
