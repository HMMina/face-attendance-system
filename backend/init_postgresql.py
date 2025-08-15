#!/usr/bin/env python3
"""
Initialize PostgreSQL database with tables and test data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.config.settings import settings
from app.models.base import Base
from app.models.employee import Employee
from app.models.attendance import Attendance
from app.models.device import Device
from app.config.database import SessionLocal
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    try:
        engine = create_engine(settings.DB_URL, echo=True)
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def add_test_data():
    """Add test data to database"""
    db = SessionLocal()
    try:
        # Clear existing data
        db.query(Attendance).delete()
        db.query(Employee).delete()
        db.query(Device).delete()
        db.commit()
        
        # Add test employees
        employees = [
            Employee(
                employee_id="EMP001",
                name="Nguyễn Văn An",
                department="IT Department"
            ),
            Employee(
                employee_id="EMP002", 
                name="Trần Thị Bích",
                department="HR Department"
            ),
            Employee(
                employee_id="EMP003",
                name="Lê Hoàng Nam",
                department="Marketing Department"
            ),
            Employee(
                employee_id="EMP004",
                name="Phạm Thị Lan",
                department="Finance Department"
            ),
            Employee(
                employee_id="EMP005",
                name="Võ Minh Đức",
                department="IT Department"
            )
        ]
        
        for emp in employees:
            db.add(emp)
        
        # Add test devices
        devices = [
            Device(
                device_id="KIOSK001",
                name="Main Entrance Kiosk",
                is_active=True
            ),
            Device(
                device_id="KIOSK002", 
                name="Office Floor 1 Kiosk",
                is_active=True
            ),
            Device(
                device_id="KIOSK003",
                name="Cafeteria Kiosk",
                is_active=False
            )
        ]
        
        for device in devices:
            db.add(device)
        
        db.commit()
        
        # Add test attendance records
        attendance_records = []
        base_time = datetime.now() - timedelta(days=7)
        
        for i in range(20):
            record = Attendance(
                employee_id=f"EMP{(i % 5) + 1:03d}",
                device_id=f"KIOSK{(i % 2) + 1:03d}",
                timestamp=base_time + timedelta(days=i % 7, hours=8 + (i % 3), minutes=i % 60),
                confidence=0.85 + (i % 15) * 0.01,
                image_path=f"./data/uploads/attendance_{i+1}.jpg"
            )
            attendance_records.append(record)
        
        for record in attendance_records:
            db.add(record)
            
        db.commit()
        
        # Print summary
        emp_count = db.query(Employee).count()
        device_count = db.query(Device).count()
        attendance_count = db.query(Attendance).count()
        
        logger.info("✅ Test data added successfully!")
        logger.info(f"📊 Summary:")
        logger.info(f"   - Employees: {emp_count}")
        logger.info(f"   - Devices: {device_count}")
        logger.info(f"   - Attendance Records: {attendance_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error adding test data: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def test_database_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        db = SessionLocal()
        result = db.execute(text("SELECT version()")).fetchone()
        db.close()
        logger.info(f"✅ PostgreSQL Connection successful!")
        logger.info(f"📋 Database version: {result[0] if result else 'Unknown'}")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Initializing PostgreSQL Database for Face Attendance System")
    print("=" * 60)
    
    # Step 1: Test connection
    print("\n1️⃣ Testing database connection...")
    if not test_database_connection():
        print("❌ Database connection failed. Please check your PostgreSQL setup.")
        sys.exit(1)
    
    # Step 2: Create tables
    print("\n2️⃣ Creating database tables...")
    if not create_tables():
        print("❌ Failed to create tables.")
        sys.exit(1)
    
    # Step 3: Add test data
    print("\n3️⃣ Adding test data...")
    if not add_test_data():
        print("❌ Failed to add test data.")
        sys.exit(1)
    
    print("\n🎉 Database initialization completed successfully!")
    print("\n🧪 You can now test the API endpoints:")
    print("   - GET  /api/v1/employees")
    print("   - GET  /api/v1/devices")  
    print("   - GET  /api/v1/attendance")
    print("   - GET  /health")
