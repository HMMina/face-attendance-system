@echo off
cd /d "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"
echo Starting KIOSK002 on port 8083...
start "KIOSK002" cmd /k "flutter run -d chrome --web-port 8083"
timeout /t 5 /nobreak > nul
echo Opening browser for KIOSK002...
start "" "chrome.exe" --new-window --app="http://localhost:8083?device_id=KIOSK002"
echo KIOSK002 is running at: http://localhost:8083?device_id=KIOSK002
pause
