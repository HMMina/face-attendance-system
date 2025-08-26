@echo off
REM Quick start for KIOSK004 using universal script
echo Starting KIOSK004 with auto-assigned port...
powershell.exe -ExecutionPolicy Bypass -File "run_universal_kiosk.ps1" -DeviceId KIOSK004
