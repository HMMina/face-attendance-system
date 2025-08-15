/// Widget hiển thị trạng thái kết nối server
import 'package:flutter/material.dart';

class ServerStatus extends StatelessWidget {
  final bool connected;
  final String? serverIp;
  const ServerStatus({super.key, required this.connected, this.serverIp});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(connected ? Icons.cloud_done : Icons.cloud_off, color: connected ? Colors.green : Colors.red),
        const SizedBox(width: 8),
        Text(connected ? 'Đã kết nối server: $serverIp' : 'Mất kết nối server'),
      ],
    );
  }
}
