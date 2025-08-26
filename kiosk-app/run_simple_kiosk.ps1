param(
    [string]$DeviceId,
    [int]$Port = 0,
    [switch]$Help,
    [switch]$List
)

if ($Help) {
    Write-Host "Universal Kiosk Runner v2.0" -ForegroundColor Green
    Write-Host "Usage: .\run_simple_kiosk.ps1 -DeviceId KIOSK001" -ForegroundColor Yellow
    exit
}

if ($List) {
    Write-Host "Available Devices:" -ForegroundColor Green
    Write-Host "  KIOSK001 → Port 8082"
    Write-Host "  KIOSK002 → Port 8083"
    Write-Host "  KIOSK003 → Port 8084"
    exit
}

if (-not $DeviceId) {
    Write-Host "Error: DeviceId required!" -ForegroundColor Red
    exit 1
}

# Simple port assignment
$assignedPort = 8082
if ($DeviceId -eq "KIOSK001") { $assignedPort = 8082 }
elseif ($DeviceId -eq "KIOSK002") { $assignedPort = 8083 }
elseif ($DeviceId -eq "KIOSK003") { $assignedPort = 8084 }
elseif ($DeviceId -match "KIOSK(\d+)") { 
    $num = [int]$matches[1]
    $assignedPort = 8081 + $num 
}

if ($Port -gt 0) { $assignedPort = $Port }

Write-Host "Starting $DeviceId on port $assignedPort" -ForegroundColor Green

Set-Location "C:\Users\ADMIN\.vscode\face-attendace-system\kiosk-app"

$url = "http://localhost:$assignedPort/?device_id=$DeviceId"
Write-Host "URL: $url" -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-Command", "flutter run -d chrome --web-port $assignedPort" -WindowStyle Normal
Start-Sleep 5
Start-Process chrome -ArgumentList "--new-window", "--app=$url"

Write-Host "Kiosk $DeviceId started!" -ForegroundColor Green
