@echo off
echo Testing Universal Kiosk Runner...
echo.

echo === HELP TEST ===
powershell.exe -ExecutionPolicy Bypass -File "run_universal_kiosk.ps1" -Help
echo.

echo === LIST TEST ===
powershell.exe -ExecutionPolicy Bypass -File "run_universal_kiosk.ps1" -List
echo.

echo === AUTO PORT TEST ===
echo This would start KIOSK003 on auto-assigned port 8084:
echo powershell.exe -ExecutionPolicy Bypass -File "run_universal_kiosk.ps1" -DeviceId KIOSK003
echo.

pause
