/// Model thông tin server phát hiện qua mDNS
class ServerInfo {
  final String serviceName;
  final String serviceType;
  final String ipAddress;
  final int port;

  ServerInfo({required this.serviceName, required this.serviceType, required this.ipAddress, required this.port});
}
