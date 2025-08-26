@echo off
REM Quick start for KIOSK005 using simple universal script
echo Starting KIOSK005 with auto-assigned port...
powershell.exe -ExecutionPolicy Bypass -File "run_simple_kiosk.ps1" -DeviceId KIOSK005
