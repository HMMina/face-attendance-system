/// Model thiết bị kiosk
class Device {
  final String deviceId;
  final String name;
  final String? ipAddress;
  final String? token;

  Device({required this.deviceId, required this.name, this.ipAddress, this.token});
}
