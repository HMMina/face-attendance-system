/// Widget hiển thị trạng thái mạng
import 'package:flutter/material.dart';

class NetworkStatus extends StatelessWidget {
  final bool connected;
  const NetworkStatus({super.key, required this.connected});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(connected ? Icons.wifi : Icons.wifi_off, color: connected ? Colors.blue : Colors.grey),
        const SizedBox(width: 8),
        Text(connected ? 'Đã kết nối WiFi' : 'Mất kết nối WiFi'),
      ],
    );
  }
}
