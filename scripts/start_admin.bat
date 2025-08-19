@echo off
echo ========================================
echo  Face Attendance System - Admin Setup
echo ========================================
echo.

echo [1/4] Kiểm tra Python và môi trường...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy! Vui lòng cài đặt Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python đã sẵn sàng

echo.
echo [2/4] Cài đặt dependencies cho Backend...
cd /d "%~dp0..\backend"
if not exist "venv" (
    echo 📦 Tạo virtual environment...
    python -m venv venv
)

echo 🔧 Kích hoạt virtual environment...
call venv\Scripts\activate.bat

echo 📦 Cài đặt packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Không thể cài đặt dependencies!
    pause
    exit /b 1
)

echo ✅ Backend dependencies đã được cài đặt

echo.
echo [3/4] Thiết lập database...
echo 🗄️ Chạy database migrations...
call alembic upgrade head
if errorlevel 1 (
    echo ⚠️ Database migration thất bại - có thể database chưa được setup
    echo ℹ️ Bạn có thể chạy lại sau khi cấu hình database
)

echo.
echo [4/4] Khởi động hệ thống...
echo 🚀 Đang khởi động Face Attendance System...
echo.
echo ========================================
echo  🌐 Admin Dashboard: http://localhost:8000/admin
echo  📚 API Documentation: http://localhost:8000/docs
echo  🔧 API Base URL: http://localhost:8000/api/v1
echo ========================================
echo.
echo Press Ctrl+C để dừng server
echo.

start http://localhost:8000/admin

python start_server.py

pause
