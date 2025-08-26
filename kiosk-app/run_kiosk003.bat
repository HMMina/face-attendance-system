@echo off
REM Quick start for KIOSK003 using universal script
echo Starting KIOSK003 with auto-assigned port...
powershell.exe -ExecutionPolicy Bypass -File "run_universal_kiosk.ps1" -DeviceId KIOSK003
