/// Service discovery qua mDNS với error handling
import 'dart:async';
import 'package:http/http.dart' as http;

class DiscoveryService {
  static String? _cachedServerUrl;
  static const Duration _discoveryTimeout = Duration(seconds: 5);
  
  /// Get server URL với caching và fallback
  static Future<String?> getServerUrl() async {
    print('DiscoveryService: Starting server discovery...');
    
    // Return cached URL if available
    if (_cachedServerUrl != null) {
      print('DiscoveryService: Testing cached URL: $_cachedServerUrl');
      final isReachable = await _testUrl(_cachedServerUrl!);
      if (isReachable) {
        print('DiscoveryService: Cached URL is reachable');
        return _cachedServerUrl;
      }
      print('DiscoveryService: Cached URL is not reachable, clearing cache');
      _cachedServerUrl = null; // Clear invalid cache
    }
    
    // Try to discover server
    print('DiscoveryService: Attempting server discovery...');
    final discoveredUrl = await discoverServer();
    if (discoveredUrl != null) {
      print('DiscoveryService: Server discovered at: $discoveredUrl');
      _cachedServerUrl = discoveredUrl;
      return discoveredUrl;
    }
    
    // Fallback to common localhost and LAN IPs
    print('DiscoveryService: Discovery failed, trying fallback URLs...');
    const fallbackUrls = [
      'http://localhost:8000',       // Local development
      'http://127.0.0.1:8000',      // Local loopback
      'http://10.0.2.2:8000',       // Android emulator
      'http://192.168.1.100:8000',  // Common LAN IP
      'http://192.168.0.100:8000',  // Alternative LAN IP
    ];
    
    for (final fallbackUrl in fallbackUrls) {
      print('DiscoveryService: Testing fallback URL: $fallbackUrl');
      final isReachable = await _testUrl(fallbackUrl);
      if (isReachable) {
        print('DiscoveryService: Fallback URL is reachable: $fallbackUrl');
        _cachedServerUrl = fallbackUrl;
        return fallbackUrl;
      }
    }

    print('DiscoveryService: All discovery attempts failed');
    return null;
  }  /// mDNS discovery với timeout
  static Future<String?> discoverServer() async {
    try {
      // TODO: Implement real mDNS discovery
      // For now, try common local network IPs
      final commonIPs = [
        'http://10.0.2.2:8000',      // Android emulator localhost
        'http://localhost:8000',      // Real device localhost
        'http://192.168.1.10:8000',
        'http://192.168.1.100:8000', 
        'http://192.168.0.10:8000',
        'http://10.0.0.10:8000',
      ];
      
      for (final ip in commonIPs) {
        print('DiscoveryService: Testing IP: $ip');
        final isReachable = await _testUrl(ip);
        if (isReachable) {
          print('DiscoveryService: Found reachable server at: $ip');
          return ip;
        }
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
