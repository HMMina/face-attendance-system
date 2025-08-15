/// Widget hiển thị trạng thái thành công/lỗi
import 'package:flutter/material.dart';

class StatusIndicator extends StatelessWidget {
  final bool success;
  final String message;
  const StatusIndicator({super.key, required this.success, required this.message});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(success ? Icons.check_circle : Icons.error, color: success ? Colors.green : Colors.red),
        const SizedBox(width: 8),
        Text(message, style: TextStyle(color: success ? Colors.green : Colors.red)),
      ],
    );
  }
}
