@echo off
cd /d "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"
echo Starting KIOSK001 on port 8082...
start "KIOSK001" cmd /k "flutter run -d chrome --web-port 8082"
timeout /t 5 /nobreak > nul
echo Opening browser for KIOSK001...
start "" "chrome.exe" --new-window --app="http://localhost:8082?device_id=KIOSK001"
echo KIOSK001 is running at: http://localhost:8082?device_id=KIOSK001
pause
