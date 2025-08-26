# Universal Kiosk Runner v2.0 - Clean Version
param(
    [string]$DeviceId,
    [int]$Port = 0,
    [switch]$Help,
    [switch]$List
)

# Port mapping for known devices
$DevicePortMap = @{
    'KIOSK001' = 8082
    'KIOSK002' = 8083  
    'KIOSK003' = 8084
    'KIOSK004' = 8085
    'KIOSK005' = 8086
}

# Base port for auto-calculation
$BasePort = 8082

function Get-DevicePort {
    param([string]$DeviceId)
    
    # If explicitly mapped, use that
    if ($DevicePortMap.ContainsKey($DeviceId)) {
        return $DevicePortMap[$DeviceId]
    }
    
    # Auto-calculate for KIOSK### pattern
    if ($DeviceId -match 'KIOSK(\d{3})') {
        $number = [int]$matches[1]
        return $BasePort + ($number - 1)
    }
    
    # Fallback: hash-based assignment
    $hash = [System.Text.Encoding]::UTF8.GetBytes($DeviceId) | ForEach-Object { $_ } | Measure-Object -Sum | Select-Object -ExpandProperty Sum
    return $BasePort + ($hash % 100)
}

function Show-Help {
    Write-Host "Universal Kiosk Runner v2.0" -ForegroundColor Green
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\run_universal_kiosk_v2.ps1 -DeviceId KIOSK001"
    Write-Host "  .\run_universal_kiosk_v2.ps1 -DeviceId KIOSK002 -Port 8084"
    Write-Host "  .\run_universal_kiosk_v2.ps1 -List"
    Write-Host ""
    Write-Host "PARAMETERS:" -ForegroundColor Yellow
    Write-Host "  -DeviceId    Device ID (KIOSK001, KIOSK002, etc.)"
    Write-Host "  -Port        Custom port (auto-assigned if not specified)"
    Write-Host "  -List        Show available devices and their ports"
    Write-Host "  -Help        Show this help message"
    Write-Host ""
    Write-Host "AUTO PORT ASSIGNMENT:" -ForegroundColor Yellow
    Write-Host "  KIOSK001 → Port 8082"
    Write-Host "  KIOSK002 → Port 8083"
    Write-Host "  KIOSK003 → Port 8084"
    Write-Host "  KIOSK### → Port 8081 + device_number"
}

function Show-DeviceList {
    Write-Host "Available Devices and Ports:" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    
    # Show predefined devices
    foreach ($device in $DevicePortMap.GetEnumerator() | Sort-Object Name) {
        $port = $device.Value
        $status = "🔴 STOPPED"
        try {
            $connection = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
            if ($connection) {
                $status = "🟢 RUNNING"
            }
        } catch {
            # Port not in use
        }
        Write-Host "  $($device.Key.PadRight(10)) → Port $port  [$status]" -ForegroundColor White
    }
    
    # Show auto-assignment pattern
    Write-Host ""
    Write-Host "Auto-Assignment Pattern:" -ForegroundColor Yellow
    Write-Host "  KIOSK006 → Port 8087"
    Write-Host "  KIOSK007 → Port 8088"
    Write-Host "  KIOSK### → Port 8081 + device_number"
}

# Handle command line arguments
if ($Help) {
    Show-Help
    exit
}

if ($List) {
    Show-DeviceList
    exit
}

if (-not $DeviceId) {
    Write-Host "❌ Error: DeviceId is required!" -ForegroundColor Red
    Write-Host ""
    Show-Help
    exit 1
}

# Determine port
if ($Port -eq 0) {
    $Port = Get-DevicePort $DeviceId
}

Write-Host "🚀 Starting Kiosk..." -ForegroundColor Green
Write-Host "   Device ID: $DeviceId" -ForegroundColor Cyan
Write-Host "   Port: $Port" -ForegroundColor Cyan

# Navigate to kiosk-app
$originalLocation = Get-Location
Set-Location "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"

# Check if port is available
try {
    $portInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($portInUse) {
        Write-Host "⚠️  Port $Port is already in use. Finding alternative..." -ForegroundColor Yellow
        # Try next available port
        for ($i = $Port + 1; $i -le $Port + 20; $i++) {
            $testPort = Get-NetTCPConnection -LocalPort $i -ErrorAction SilentlyContinue
            if (-not $testPort) {
                $Port = $i
                Write-Host "✅ Using alternative port: $Port" -ForegroundColor Green
                break
            }
        }
    }
} catch {
    # Port checking failed, continue anyway
}

# Start Flutter
Write-Host "🔧 Starting Flutter on port $Port..." -ForegroundColor Yellow

# Generate URLs
$directUrl = "http://localhost:$Port"
$deviceUrl = "http://localhost:$Port/?device_id=$DeviceId"

Write-Host "🌐 URLs:" -ForegroundColor Green
Write-Host "   Direct URL: $directUrl" -ForegroundColor White
Write-Host "   Device URL: $deviceUrl" -ForegroundColor White

# Start Flutter in background
Start-Process powershell -ArgumentList "-Command", "flutter run -d chrome --web-port $Port" -WindowStyle Normal

# Wait for Flutter to start
Write-Host "⏳ Waiting for Flutter to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

# Open browser with device ID
Write-Host "🌐 Opening browser..." -ForegroundColor Green
Start-Process "chrome.exe" -ArgumentList "--new-window", "--app=$deviceUrl"

Write-Host "✅ Kiosk $DeviceId is running on port $Port!" -ForegroundColor Green
Write-Host "📱 To create more devices, run:" -ForegroundColor Cyan
Write-Host "   .\run_universal_kiosk_v2.ps1 -DeviceId KIOSK006" -ForegroundColor White
Write-Host "   .\run_universal_kiosk_v2.ps1 -DeviceId KIOSK007" -ForegroundColor White

# Return to original location
Set-Location $originalLocation
