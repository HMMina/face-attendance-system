@echo off
REM Script để chạy Kiosk App với device_id cụ thể
REM Sử dụng: run_kiosk.bat KIOSK001

if "%1"=="" (
    echo Usage: run_kiosk.bat ^<DEVICE_ID^>
    echo Example: run_kiosk.bat KIOSK001
    echo.
    echo Available devices in database:
    echo - KIOSK001 ^(IT^)
    echo - KIOSK002 ^(IT2^)  
    echo - KIOSK003 ^(IT^)
    echo - KIOSK004 ^(IT^)
    echo - KIOSK_001 ^(Cổng chính^)
    echo - KIOSK_002 ^(Kiosk Tầng 3^)
    pause
    exit /b 1
)

set DEVICE_ID=%1
echo ===============================================
echo Starting Kiosk App with Device ID: %DEVICE_ID%
echo ===============================================

REM Set environment variables
set KIOSK_DEVICE_ID=%DEVICE_ID%
set KIOSK_TEST_MODE=true

REM Navigate to kiosk-app directory
cd /d "%~dp0"

REM Start Flutter app
echo Starting Flutter app on Chrome (port 8082)...
flutter run -d chrome --web-port 8082

pause
