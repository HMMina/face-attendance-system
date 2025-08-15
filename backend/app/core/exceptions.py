"""
Custom exceptions and error handlers - Optimized
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class FaceAttendanceException(Exception):
    """Base exception for Face Attendance System"""
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(FaceAttendanceException):
    """Database related exceptions"""
    pass


class ValidationException(FaceAttendanceException):
    """Validation related exceptions"""
    pass


class AuthenticationException(FaceAttendanceException):
    """Authentication related exceptions"""
    pass


class AuthorizationException(FaceAttendanceException):
    """Authorization related exceptions"""
    pass


class FileException(FaceAttendanceException):
    """File handling related exceptions"""
    pass


class FaceRecognitionException(FaceAttendanceException):
    """Face recognition related exceptions"""
    pass


class DeviceException(FaceAttendanceException):
    """Device related exceptions"""
    pass


# HTTP Exception classes for API responses
class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictException(HTTPException):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class UnprocessableEntityException(HTTPException):
    def __init__(self, detail: str = "Unprocessable entity"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class InternalServerErrorException(HTTPException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


# Error code constants
class ErrorCodes:
    # Database errors
    DATABASE_CONNECTION_ERROR = "DB_CONNECTION_ERROR"
    DATABASE_QUERY_ERROR = "DB_QUERY_ERROR"
    RECORD_NOT_FOUND = "RECORD_NOT_FOUND"
    DUPLICATE_RECORD = "DUPLICATE_RECORD"
    
    # Authentication errors
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # Authorization errors
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    ACCESS_DENIED = "ACCESS_DENIED"
    
    # Validation errors
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    INVALID_FORMAT = "INVALID_FORMAT"
    
    # File errors
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_UPLOAD_ERROR = "FILE_UPLOAD_ERROR"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    
    # Face recognition errors
    NO_FACE_DETECTED = "NO_FACE_DETECTED"
    MULTIPLE_FACES_DETECTED = "MULTIPLE_FACES_DETECTED"
    FACE_RECOGNITION_FAILED = "FACE_RECOGNITION_FAILED"
    LOW_RECOGNITION_CONFIDENCE = "LOW_RECOGNITION_CONFIDENCE"
    
    # Device errors
    DEVICE_NOT_FOUND = "DEVICE_NOT_FOUND"
    DEVICE_OFFLINE = "DEVICE_OFFLINE"
    DEVICE_REGISTRATION_FAILED = "DEVICE_REGISTRATION_FAILED"
    
    # Business logic errors
    EMPLOYEE_NOT_FOUND = "EMPLOYEE_NOT_FOUND"
    ATTENDANCE_ALREADY_RECORDED = "ATTENDANCE_ALREADY_RECORDED"
    INVALID_ATTENDANCE_TIME = "INVALID_ATTENDANCE_TIME"


# Predefined error messages
ERROR_MESSAGES = {
    ErrorCodes.DATABASE_CONNECTION_ERROR: "Unable to connect to database",
    ErrorCodes.DATABASE_QUERY_ERROR: "Database query failed",
    ErrorCodes.RECORD_NOT_FOUND: "Record not found",
    ErrorCodes.DUPLICATE_RECORD: "Record already exists",
    
    ErrorCodes.INVALID_CREDENTIALS: "Invalid username or password",
    ErrorCodes.TOKEN_EXPIRED: "Authentication token has expired",
    ErrorCodes.INVALID_TOKEN: "Invalid authentication token",
    
    ErrorCodes.INSUFFICIENT_PERMISSIONS: "Insufficient permissions to perform this action",
    ErrorCodes.ACCESS_DENIED: "Access denied",
    
    ErrorCodes.INVALID_INPUT: "Invalid input provided",
    ErrorCodes.MISSING_REQUIRED_FIELD: "Required field is missing",
    ErrorCodes.INVALID_FORMAT: "Invalid data format",
    
    ErrorCodes.FILE_TOO_LARGE: "File size exceeds maximum limit",
    ErrorCodes.INVALID_FILE_TYPE: "Invalid file type",
    ErrorCodes.FILE_UPLOAD_ERROR: "Failed to upload file",
    ErrorCodes.FILE_NOT_FOUND: "File not found",
    
    ErrorCodes.NO_FACE_DETECTED: "No face detected in the image",
    ErrorCodes.MULTIPLE_FACES_DETECTED: "Multiple faces detected, please ensure only one person",
    ErrorCodes.FACE_RECOGNITION_FAILED: "Face recognition failed",
    ErrorCodes.LOW_RECOGNITION_CONFIDENCE: "Low recognition confidence, please try again",
    
    ErrorCodes.DEVICE_NOT_FOUND: "Device not found",
    ErrorCodes.DEVICE_OFFLINE: "Device is offline",
    ErrorCodes.DEVICE_REGISTRATION_FAILED: "Device registration failed",
    
    ErrorCodes.EMPLOYEE_NOT_FOUND: "Employee not found",
    ErrorCodes.ATTENDANCE_ALREADY_RECORDED: "Attendance already recorded for this time period",
    ErrorCodes.INVALID_ATTENDANCE_TIME: "Invalid attendance time",
}


def get_error_message(error_code: str, default: str = "An error occurred") -> str:
    """Get error message by error code"""
    return ERROR_MESSAGES.get(error_code, default)
