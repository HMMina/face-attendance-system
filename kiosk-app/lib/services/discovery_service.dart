/// Service discovery qua mDNS với error handling
import 'dart:async';
import 'package:http/http.dart' as http;

class DiscoveryService {
  static String? _cachedServerUrl;
  static const Duration _discoveryTimeout = Duration(seconds: 5);
  
  /// Get server URL với caching và fallback
  static Future<String?> getServerUrl() async {
    // Return cached URL if available
    if (_cachedServerUrl != null) {
      final isReachable = await _testUrl(_cachedServerUrl!);
      if (isReachable) return _cachedServerUrl;
      _cachedServerUrl = null; // Clear invalid cache
    }
    
    // Try to discover server
    final discoveredUrl = await discoverServer();
    if (discoveredUrl != null) {
      _cachedServerUrl = discoveredUrl;
      return discoveredUrl;
    }
    
    // Fallback to default localhost
    const fallbackUrl = 'http://localhost:8000';
    final isReachable = await _testUrl(fallbackUrl);
    if (isReachable) {
      _cachedServerUrl = fallbackUrl;
      return fallbackUrl;
    }
    
    return null;
  }
  
  /// mDNS discovery với timeout
  static Future<String?> discoverServer() async {
    try {
      // TODO: Implement real mDNS discovery
      // For now, try common local network IPs
      final commonIPs = [
        'http://192.168.1.10:8000',
        'http://192.168.1.100:8000', 
        'http://192.168.0.10:8000',
        'http://10.0.0.10:8000',
      ];
      
      for (final ip in commonIPs) {
        final isReachable = await _testUrl(ip);
        if (isReachable) return ip;
      }
      
      return null;
    } catch (e) {
      print('Discovery error: $e');
      return null;
    }
  }
  
  /// Test if URL is reachable
  static Future<bool> _testUrl(String url) async {
    try {
      final response = await http.get(
        Uri.parse('$url/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_discoveryTimeout);
      
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
  
  /// Clear cached server URL
  static void clearCache() {
    _cachedServerUrl = null;
  }
}
