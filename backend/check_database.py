#!/usr/bin/env python3
"""
Script kiểm tra trạng thái database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.face_template import FaceTemplate
from app.models.employee import Employee

def check_database():
    try:
        print("🔍 Đang kiểm tra kết nối database...")
        db = SessionLocal()
        
        # Đếm số lượng records
        employee_count = db.query(Employee).count()
        template_count = db.query(FaceTemplate).count()
        
        print(f"✅ Database kết nối thành công!")
        print(f"📊 Số lượng employees: {employee_count}")
        print(f"📊 Số lượng face templates: {template_count}")
        
        if template_count == 0:
            print("\n⚠️  CẢNH BÁO: Bảng face_templates TRỐNG!")
            print("   🔹 Đây có thể là nguyên nhân gây lỗi upload ảnh")
            print("   🔹 Hệ thống cần có ít nhất một face template để hoạt động đúng")
            
            if employee_count > 0:
                print(f"\n💡 Giải pháp: Có {employee_count} employees nhưng chưa có face templates")
                print("   👉 Cần upload ảnh cho các nhân viên để tạo face templates")
        else:
            print("✅ Face templates có dữ liệu - hệ thống hoạt động bình thường")
            
            # Liệt kê một vài face templates
            templates = db.query(FaceTemplate).limit(5).all()
            print(f"\n📋 Face templates mẫu:")
            for tmpl in templates:
                print(f"   - Employee {tmpl.employee_id}: image_id={tmpl.image_id}, file={tmpl.filename}")
        
        # Kiểm tra employees
        if employee_count > 0:
            print(f"\n👥 Employees mẫu:")
            employees = db.query(Employee).limit(3).all()
            for emp in employees:
                # Sử dụng emp.employee_id (string) thay vì emp.id (integer)
                emp_templates = db.query(FaceTemplate).filter(FaceTemplate.employee_id == emp.employee_id).count()
                print(f"   - {emp.name} (Employee ID: {emp.employee_id}, DB ID: {emp.id}) - {emp_templates} face templates")
        else:
            print("\n⚠️  Không có employee nào trong database!")
        
        db.close()
        return template_count > 0
        
    except Exception as e:
        print(f"❌ Lỗi database: {e}")
        print(f"   Chi tiết: {type(e).__name__}")
        return False

if __name__ == "__main__":
    has_templates = check_database()
    if not has_templates:
        print("\n🚨 HỆ THỐNG CẦN KHẮC PHỤC:")
        print("   1. Bảng face_templates trống")
        print("   2. Cần upload ảnh cho nhân viên để tạo face templates")
        print("   3. Đây có thể là nguyên nhân admin dashboard không kết nối được")
