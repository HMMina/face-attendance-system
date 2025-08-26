# Script to run kiosk instances with specific device IDs
param(
    [string]$DeviceId = "KIOSK001",
    [int]$Port = 8082,
    [switch]$Help
)

if ($Help) {
    Write-Host "🚀 KIOSK APP RUNNER" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\run_kiosk_multiple.ps1 -DeviceId KIOSK001 -Port 8082"
    Write-Host "  .\run_kiosk_multiple.ps1 -DeviceId KIOSK002 -Port 8083"
    Write-Host ""
    Write-Host "Quick commands:" -ForegroundColor Cyan
    Write-Host "  .\run_kiosk_multiple.ps1 KIOSK001    # Run KIOSK001 on port 8082"
    Write-Host "  .\run_kiosk_multiple.ps1 KIOSK002    # Run KIOSK002 on port 8083"
    Write-Host ""
    exit
}

# Auto-assign ports based on device ID
if ($DeviceId -eq "KIOSK002" -and $Port -eq 8082) { $Port = 8083 }

Write-Host "� Starting Kiosk App..." -ForegroundColor Green
Write-Host "   Device ID: $DeviceId" -ForegroundColor Cyan
Write-Host "   Port: $Port" -ForegroundColor Cyan

# Navigate to kiosk-app directory
Push-Location "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"

# Start Flutter
Write-Host "🔧 Starting Flutter on port $Port..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "flutter run -d chrome --web-port $Port" -WindowStyle Normal

# Wait for Flutter to start
Write-Host "⏳ Waiting for Flutter to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Open browser with device ID
$url = "http://localhost:$Port/?device_id=$DeviceId"
Write-Host "🌐 Opening browser: $url" -ForegroundColor Green

Start-Process "chrome.exe" -ArgumentList "--new-window", "--app=$url"

Write-Host "✅ Kiosk $DeviceId is now running on $url" -ForegroundColor Green

Pop-Location
