/// Custom exceptions for the application
class AppException implements Exception {
  final String message;
  final String? code;
  
  const AppException({
    required this.message,
    this.code,
  });
  
  @override
  String toString() => 'AppException: $message${code != null ? ' (Code: $code)' : ''}';
}

/// Network related exceptions
class NetworkException extends AppException {
  final int? statusCode;
  
  const NetworkException({
    required String message,
    String? code,
    this.statusCode,
  }) : super(message: message, code: code);
  
  @override
  String toString() => 'NetworkException: $message${statusCode != null ? ' (Status: $statusCode)' : ''}';
}

/// Camera related exceptions
class CameraException extends AppException {
  const CameraException({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

/// Face recognition exceptions
class FaceRecognitionException extends AppException {
  const FaceRecognitionException({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

/// Device related exceptions
class DeviceException extends AppException {
  const DeviceException({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}

/// Storage related exceptions
class StorageException extends AppException {
  const StorageException({
    required String message,
    String? code,
  }) : super(message: message, code: code);
}
