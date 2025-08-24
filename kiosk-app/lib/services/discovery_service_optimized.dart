/// Service discovery qua mDNS với error handling - Multi-Kiosk Optimized
import 'dart:async';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class DiscoveryService {
  static String? _cachedServerUrl;
  static DateTime? _cacheTimestamp;
  static const Duration _discoveryTimeout = Duration(seconds: 5);
  static const Duration _cacheValidDuration = Duration(hours: 1);
  
  /// Get server URL với persistent caching và fallback optimized cho multi-kiosk
  static Future<String?> getServerUrl() async {
    print('DiscoveryService: Starting server discovery...');
    
    // Check if cached URL is still valid (time-based)
    if (_cachedServerUrl != null && _cacheTimestamp != null) {
      if (DateTime.now().difference(_cacheTimestamp!) < _cacheValidDuration) {
        print('DiscoveryService: Using time-valid cached URL: $_cachedServerUrl');
        final isReachable = await _testUrl(_cachedServerUrl!);
        if (isReachable) {
          return _cachedServerUrl;
        }
      }
    }
    
    // Try to load from persistent storage
    final persistentUrl = await _loadPersistedUrl();
    if (persistentUrl != null) {
      print('DiscoveryService: Testing persisted URL: $persistentUrl');
      final isReachable = await _testUrl(persistentUrl);
      if (isReachable) {
        _updateCache(persistentUrl);
        return persistentUrl;
      }
    }
    
    // Try to discover server with optimized IP ranges
    print('DiscoveryService: Attempting server discovery...');
    final discoveredUrl = await discoverServerOptimized();
    if (discoveredUrl != null) {
      print('DiscoveryService: Server discovered at: $discoveredUrl');
      _updateCache(discoveredUrl);
      await _persistUrl(discoveredUrl);
      return discoveredUrl;
    }
    
    // Enhanced fallback with more common network configurations
    print('DiscoveryService: Discovery failed, trying enhanced fallback URLs...');
    final fallbackUrl = await _tryEnhancedFallbacks();
    if (fallbackUrl != null) {
      _updateCache(fallbackUrl);
      await _persistUrl(fallbackUrl);
      return fallbackUrl;
    }

    print('DiscoveryService: All discovery attempts failed');
    return null;
  }
  
  /// Optimized server discovery with network detection
  static Future<String?> discoverServerOptimized() async {
    try {
      // Get local network info for smarter discovery
      final localIPs = await _getLocalNetworkRange();
      
      // Combine with common development IPs
      final testIPs = [
        ...localIPs,
        'http://10.0.2.2:8000',      // Android emulator localhost
        'http://localhost:8000',      // Real device localhost
        'http://127.0.0.1:8000',     // Loopback
        'http://192.168.1.1:8000',   // Common router IP
        'http://192.168.0.1:8000',   // Alternative router IP
      ];
      
      // Test IPs in parallel for faster discovery
      final futures = testIPs.map((ip) => _testUrlWithResult(ip));
      final results = await Future.wait(futures);
      
      // Return first successful URL
      for (int i = 0; i < results.length; i++) {
        if (results[i]) {
          print('DiscoveryService: Found reachable server at: ${testIPs[i]}');
          return testIPs[i];
        }
      }
      
      return null;
    } catch (e) {
      print('DiscoveryService: Error in optimized discovery: $e');
      return null;
    }
  }
  
  static Future<List<String>> _getLocalNetworkRange() async {
    try {
      final interfaces = await NetworkInterface.list();
      final localIPs = <String>[];
      
      for (final interface in interfaces) {
        for (final addr in interface.addresses) {
          if (addr.type == InternetAddressType.IPv4 && !addr.isLoopback) {
            final ip = addr.address;
            final parts = ip.split('.');
            if (parts.length == 4) {
              // Generate common IPs in the same subnet
              final subnet = '${parts[0]}.${parts[1]}.${parts[2]}';
              localIPs.addAll([
                'http://$subnet.1:8000',    // Router
                'http://$subnet.10:8000',   // Common static IP
                'http://$subnet.100:8000',  // Common static IP
                'http://$subnet.101:8000',  // Common static IP
                'http://$ip:8000',          // This device IP
              ]);
            }
          }
        }
      }
      
      return localIPs.toSet().toList(); // Remove duplicates
    } catch (e) {
      print('DiscoveryService: Failed to get local network range: $e');
      return [];
    }
  }
  
  static Future<String?> _tryEnhancedFallbacks() async {
    const fallbackUrls = [
      'http://localhost:8000',       // Local development
      'http://127.0.0.1:8000',      // Local loopback
      'http://10.0.2.2:8000',       // Android emulator
      'http://192.168.1.100:8000',  // Common LAN IP
      'http://192.168.0.100:8000',  // Alternative LAN IP
      'http://192.168.1.10:8000',   // Server IP
      'http://192.168.0.10:8000',   // Alternative server IP
      'http://10.0.0.10:8000',      // Corporate network
      'http://172.16.0.10:8000',    // Docker/VPN network
    ];
    
    for (final fallbackUrl in fallbackUrls) {
      print('DiscoveryService: Testing fallback URL: $fallbackUrl');
      final isReachable = await _testUrl(fallbackUrl);
      if (isReachable) {
        print('DiscoveryService: Fallback URL is reachable: $fallbackUrl');
        return fallbackUrl;
      }
    }
    
    return null;
  }
  
  static void _updateCache(String url) {
    _cachedServerUrl = url;
    _cacheTimestamp = DateTime.now();
  }
  
  static Future<void> _persistUrl(String url) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('server_url', url);
      await prefs.setInt('server_url_timestamp', DateTime.now().millisecondsSinceEpoch);
    } catch (e) {
      print('DiscoveryService: Failed to persist URL: $e');
    }
  }
  
  static Future<String?> _loadPersistedUrl() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final url = prefs.getString('server_url');
      final timestamp = prefs.getInt('server_url_timestamp');
      
      if (url != null && timestamp != null) {
        final persistedTime = DateTime.fromMillisecondsSinceEpoch(timestamp);
        if (DateTime.now().difference(persistedTime) < Duration(days: 1)) {
          return url;
        }
      }
    } catch (e) {
      print('DiscoveryService: Failed to load persisted URL: $e');
    }
    return null;
  }

  /// Test URL và trả về boolean
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
  
  /// Test URL và trả về kết quả với thông tin chi tiết
  static Future<bool> _testUrlWithResult(String url) async {
    try {
      final response = await http.get(
        Uri.parse('$url/health'),
        headers: {'Content-Type': 'application/json'},
      ).timeout(_discoveryTimeout);
      
      final success = response.statusCode == 200;
      if (success) {
        print('DiscoveryService: ✅ $url is reachable');
      }
      return success;
    } catch (e) {
      return false;
    }
  }
  
  /// Clear all cached URLs (useful for troubleshooting)
  static Future<void> clearCache() async {
    _cachedServerUrl = null;
    _cacheTimestamp = null;
    
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('server_url');
      await prefs.remove('server_url_timestamp');
      print('DiscoveryService: Cache cleared');
    } catch (e) {
      print('DiscoveryService: Failed to clear cache: $e');
    }
  }
  
  /// Force rediscovery (bypass cache)
  static Future<String?> forceRediscovery() async {
    await clearCache();
    return await getServerUrl();
  }
  
  /// Get cached URL (có thể null)
  static String? getCachedUrl() {
    return _cachedServerUrl;
  }
}
