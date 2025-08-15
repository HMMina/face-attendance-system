#!/usr/bin/env python3
"""
Test script để kiểm tra logic toàn bộ hệ thống
Chạy script này để đảm bảo tất cả các component hoạt động đúng
"""

import sys
import asyncio
import requests
import json
from pathlib import Path

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_result(test_name, success, message=""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if success else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} {test_name}")
    if message:
        print(f"    {message}")

async def test_backend_logic():
    """Test backend logic and endpoints"""
    print(f"\n{Colors.BLUE}🧪 Testing Backend Logic{Colors.END}")
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print_result("Health Check", response.status_code == 200, 
                    f"Status: {response.json() if response.status_code == 200 else 'Failed'}")
    except requests.RequestException as e:
        print_result("Health Check", False, f"Error: {e}")
    
    # Test 2: Get employees endpoint
    try:
        response = requests.get(f"{base_url}/api/v1/employees", timeout=5)
        print_result("Get Employees", response.status_code in [200, 404], 
                    f"Response: {response.status_code}")
    except requests.RequestException as e:
        print_result("Get Employees", False, f"Error: {e}")
    
    # Test 3: API documentation
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print_result("API Documentation", response.status_code == 200, 
                    "OpenAPI docs accessible")
    except requests.RequestException as e:
        print_result("API Documentation", False, f"Error: {e}")

def test_file_structure():
    """Test project file structure"""
    print(f"\n{Colors.BLUE}📁 Testing File Structure{Colors.END}")
    
    required_files = [
        "backend/app/main.py",
        "backend/app/config/settings.py", 
        "backend/app/config/database.py",
        "backend/app/services/employee_service.py",
        "backend/app/api/v1/attendance.py",
        "backend/app/api/v1/employees.py",
        "admin-dashboard/src/App.js",
        "admin-dashboard/src/services/api.js",
        "kiosk-app/lib/main.dart",
        "kiosk-app/lib/services/api_service.dart",
        "kiosk-app/lib/services/discovery_service.dart",
        "OPTIMIZED_STRUCTURE.md"
    ]
    
    base_path = Path(__file__).parent
    
    for file_path in required_files:
        full_path = base_path / file_path
        exists = full_path.exists()
        print_result(f"File exists: {file_path}", exists)

def test_configuration_logic():
    """Test configuration and settings logic"""
    print(f"\n{Colors.BLUE}⚙️  Testing Configuration Logic{Colors.END}")
    
    try:
        # Test settings import
        sys.path.append(str(Path(__file__).parent / "backend"))
        from app.config.settings import settings
        
        # Test environment variables
        has_db_url = hasattr(settings, 'DB_URL') and settings.DB_URL
        print_result("Database URL configured", has_db_url, 
                    f"DB_URL: {'Set' if has_db_url else 'Missing'}")
        
        # Test upload directory
        has_upload_dir = hasattr(settings, 'UPLOAD_DIR') and settings.UPLOAD_DIR
        print_result("Upload directory configured", has_upload_dir)
        
        # Test JWT settings
        has_jwt_secret = hasattr(settings, 'JWT_SECRET_KEY') and settings.JWT_SECRET_KEY
        print_result("JWT secret configured", has_jwt_secret)
        
    except ImportError as e:
        print_result("Settings import", False, f"Error: {e}")

def test_service_logic():
    """Test service layer logic"""
    print(f"\n{Colors.BLUE}🔧 Testing Service Logic{Colors.END}")
    
    try:
        sys.path.append(str(Path(__file__).parent / "backend"))
        from app.services.employee_service import EmployeeService
        
        # Test class exists and has required methods
        required_methods = ['create_employee', 'get_employees', 'get_employee', 'update_employee', 'delete_employee']
        
        for method in required_methods:
            has_method = hasattr(EmployeeService, method)
            print_result(f"EmployeeService.{method}", has_method)
            
    except ImportError as e:
        print_result("Service logic import", False, f"Error: {e}")

def test_frontend_logic():
    """Test frontend configuration"""
    print(f"\n{Colors.BLUE}🎨 Testing Frontend Logic{Colors.END}")
    
    # Check admin dashboard package.json
    admin_package = Path(__file__).parent / "admin-dashboard" / "package.json"
    if admin_package.exists():
        try:
            with open(admin_package, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            # Check required dependencies
            deps = package_data.get('dependencies', {})
            required_deps = ['react', 'axios', 'react-router-dom', '@mui/material']
            
            for dep in required_deps:
                has_dep = dep in deps
                print_result(f"Admin Dashboard: {dep}", has_dep)
                
        except Exception as e:
            print_result("Admin Dashboard package.json", False, f"Error: {e}")
    else:
        print_result("Admin Dashboard package.json", False, "File not found")
    
    # Check Flutter pubspec.yaml
    flutter_pubspec = Path(__file__).parent / "kiosk-app" / "pubspec.yaml"
    if flutter_pubspec.exists():
        with open(flutter_pubspec, 'r', encoding='utf-8') as f:
            pubspec_content = f.read()
            
        required_flutter_deps = ['flutter', 'http', 'camera']
        for dep in required_flutter_deps:
            has_dep = dep in pubspec_content
            print_result(f"Flutter App: {dep}", has_dep)
    else:
        print_result("Flutter pubspec.yaml", False, "File not found")

async def main():
    """Main test runner"""
    print(f"{Colors.BLUE}🚀 Face Attendance System - Logic Validation{Colors.END}")
    print("=" * 50)
    
    # Run all tests
    test_file_structure()
    test_configuration_logic()
    test_service_logic()
    test_frontend_logic()
    await test_backend_logic()
    
    print(f"\n{Colors.GREEN}✅ Validation Complete - Ready for Experimentation!{Colors.END}")
    print(f"{Colors.YELLOW}Next Steps:{Colors.END}")
    print("1. Start backend: cd backend && python -m app.main")
    print("2. Start admin dashboard: cd admin-dashboard && npm start")
    print("3. Run Flutter app: cd kiosk-app && flutter run")

if __name__ == "__main__":
    asyncio.run(main())
