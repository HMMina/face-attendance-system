/// Màn hình tìm server qua mDNS
import 'package:flutter/material.dart';
import '../services/discovery_service.dart';
import '../config/network_config.dart';

class ServerDiscoveryScreen extends StatefulWidget {
  const ServerDiscoveryScreen({super.key});

  @override
  State<ServerDiscoveryScreen> createState() => _ServerDiscoveryScreenState();
}

class _ServerDiscoveryScreenState extends State<ServerDiscoveryScreen> {
  String? serverIp;
  bool isSearching = false;

  Future<void> _discoverServer() async {
    setState(() { isSearching = true; });
    serverIp = await DiscoveryService.discoverServer();
    setState(() { isSearching = false; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tìm Server')), 
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(serverIp != null ? 'Server IP: $serverIp' : 'Chưa tìm thấy server'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: isSearching ? null : _discoverServer,
              child: const Text('Tìm server qua mDNS'),
            ),
          ],
        ),
      ),
    );
  }
}
