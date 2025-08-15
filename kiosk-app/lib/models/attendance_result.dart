/// Model kết quả chấm công
class AttendanceResult {
  final bool success;
  final String employeeId;
  final double confidence;
  final String timestamp;

  AttendanceResult({required this.success, required this.employeeId, required this.confidence, required this.timestamp});
}
