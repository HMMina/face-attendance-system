# Script để chạy Kiosk App với device_id cụ thể
# Sử dụng: .\run_kiosk.ps1 KIOSK001

param(
    [Parameter(Mandatory=$true)]
    [string]$DeviceId
)

# Validate device_id format
if ($DeviceId -notmatch "^KIOSK\d{3}$|^KIOSK_\d{3}$") {
    Write-Host "⚠️ Warning: Device ID '$DeviceId' doesn't follow expected format (KIOSK001 or KIOSK_001)" -ForegroundColor Yellow
}

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Starting Kiosk App with Device ID: $DeviceId" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

# Set environment variables
$env:KIOSK_DEVICE_ID = $DeviceId
$env:KIOSK_TEST_MODE = "true"

Write-Host "🔧 Environment variables set:" -ForegroundColor Blue
Write-Host "   KIOSK_DEVICE_ID = $DeviceId" -ForegroundColor Gray
Write-Host "   KIOSK_TEST_MODE = true" -ForegroundColor Gray

# Navigate to script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $ScriptDir

Write-Host "📂 Working directory: $ScriptDir" -ForegroundColor Blue

# Check if pubspec.yaml exists
if (-not (Test-Path "pubspec.yaml")) {
    Write-Host "❌ Error: pubspec.yaml not found. Make sure you're in the kiosk-app directory." -ForegroundColor Red
    exit 1
}

Write-Host "🚀 Starting Flutter app on Chrome (port 8082)..." -ForegroundColor Green

try {
    # Start Flutter app
    flutter run -d chrome --web-port 8082
} catch {
    Write-Host "❌ Error starting Flutter app: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}

Write-Host "👋 Kiosk app session ended." -ForegroundColor Yellow
