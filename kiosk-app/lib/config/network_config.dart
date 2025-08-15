/// Cấu hình mạng & mDNS cho kiosk
class NetworkConfig {
  static String mdnsServiceType = '_attendance._tcp.local.';
  static int serverPort = 8000;
  static String? discoveredServerIp;
}
