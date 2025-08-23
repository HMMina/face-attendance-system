"""
Employee Deletion Service - Safe deletion with cleanup
"""
from sqlalchemy.orm import Session
from app.models.employee import Employee
from app.models.face_template import FaceTemplate
from app.models.attendance import Attendance
from pathlib import Path
import shutil
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class EmployeeDeletionService:
    """Service để xóa employee một cách an toàn với cleanup đầy đủ"""
    
    def __init__(self, db: Session):
        self.db = db
        self.photo_base_dir = Path("data/employee_photos")
    
    def delete_employee_safely(self, employee_id: str, cleanup_files: bool = True) -> Dict[str, Any]:
        """
        Xóa employee một cách an toàn với full cleanup
        
        Args:
            employee_id: ID của employee cần xóa
            cleanup_files: Có xóa files không (default: True)
            
        Returns:
            Dict chứa thông tin về quá trình xóa
        """
        
        result = {
            "success": False,
            "employee_id": employee_id,
            "deleted_records": {
                "face_templates": 0,
                "attendance_records": 0,
                "employee": 0,
                "files_cleaned": 0
            },
            "errors": [],
            "warnings": []
        }
        
        try:
            # 1. Kiểm tra employee tồn tại
            employee = self.db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if not employee:
                result["errors"].append(f"Employee {employee_id} not found")
                return result
            
            logger.info(f"Starting safe deletion for employee: {employee_id} - {employee.name}")
            
            # 2. Thu thập thông tin trước khi xóa
            face_templates_count = self.db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).count()
            
            attendance_count = self.db.query(Attendance).filter(
                Attendance.employee_id == employee_id
            ).count()
            
            logger.info(f"Found {face_templates_count} face templates and {attendance_count} attendance records")
            
            # 3. Xóa files nếu được yêu cầu
            files_deleted = 0
            if cleanup_files:
                employee_photo_dir = self.photo_base_dir / employee_id
                if employee_photo_dir.exists():
                    try:
                        # Đếm files trước khi xóa
                        files_deleted = len(list(employee_photo_dir.glob("*")))
                        shutil.rmtree(employee_photo_dir)
                        logger.info(f"Deleted employee photo directory: {employee_photo_dir}")
                    except Exception as e:
                        result["warnings"].append(f"Could not delete photo directory: {e}")
            
            # 4. Xóa employee (CASCADE sẽ tự động xóa related records)
            self.db.delete(employee)
            self.db.commit()
            
            # 5. Verify deletion
            remaining_templates = self.db.query(FaceTemplate).filter(
                FaceTemplate.employee_id == employee_id
            ).count()
            
            remaining_attendance = self.db.query(Attendance).filter(
                Attendance.employee_id == employee_id
            ).count()
            
            if remaining_templates > 0 or remaining_attendance > 0:
                result["warnings"].append(
                    f"Some records may still exist: {remaining_templates} templates, {remaining_attendance} attendance"
                )
            
            # 6. Update result
            result.update({
                "success": True,
                "deleted_records": {
                    "face_templates": face_templates_count,
                    "attendance_records": attendance_count,
                    "employee": 1,
                    "files_cleaned": files_deleted
                }
            })
            
            logger.info(f"Successfully deleted employee {employee_id}")
            
        except Exception as e:
            self.db.rollback()
            error_msg = f"Error deleting employee {employee_id}: {str(e)}"
            logger.error(error_msg)
            result["errors"].append(error_msg)
        
        return result
    
    def get_employee_deletion_preview(self, employee_id: str) -> Dict[str, Any]:
        """
        Preview những gì sẽ bị xóa khi xóa employee
        """
        
        preview = {
            "employee_id": employee_id,
            "employee_exists": False,
            "employee_name": None,
            "will_delete": {
                "face_templates": 0,
                "attendance_records": 0,
                "photo_files": 0
            },
            "photo_directory": None
        }
        
        try:
            # Check employee
            employee = self.db.query(Employee).filter(Employee.employee_id == employee_id).first()
            if employee:
                preview["employee_exists"] = True
                preview["employee_name"] = employee.name
                
                # Count related records
                preview["will_delete"]["face_templates"] = self.db.query(FaceTemplate).filter(
                    FaceTemplate.employee_id == employee_id
                ).count()
                
                preview["will_delete"]["attendance_records"] = self.db.query(Attendance).filter(
                    Attendance.employee_id == employee_id
                ).count()
                
                # Check photo files
                employee_photo_dir = self.photo_base_dir / employee_id
                if employee_photo_dir.exists():
                    preview["will_delete"]["photo_files"] = len(list(employee_photo_dir.glob("*")))
                    preview["photo_directory"] = str(employee_photo_dir)
                
        except Exception as e:
            logger.error(f"Error getting deletion preview: {e}")
        
        return preview
