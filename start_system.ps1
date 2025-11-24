# Daladala RL + 3D Render - Complete System Startup
# This script starts all system components automatically

param(
    [switch]$SkipTests = $false,
    [switch]$DontWait = $false,
    [int]$Port = 5000
)

$ErrorActionPreference = "Stop"

# Colors
$Green = @{ ForegroundColor = "Green" }
$Red = @{ ForegroundColor = "Red" }
$Yellow = @{ ForegroundColor = "Yellow" }
$Cyan = @{ ForegroundColor = "Cyan" }

Write-Host "`n" @Cyan
Write-Host "╔════════════════════════════════════════════════════════════════╗" @Cyan
Write-Host "║  DALADALA RL + 3D RENDER - SYSTEM STARTUP                     ║" @Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" @Cyan

Write-Host "`nSystem Components:" @Cyan
Write-Host "  ✓ Flask Backend (RL Environment)    - Port 5000"
Write-Host "  ✓ React Frontend (3D Render)        - Port 5173"
Write-Host "  ✓ WebSocket Bridge (Socket.IO)      - Dynamic"
Write-Host ""

# Define paths
$ProjectRoot = "c:\Users\Excel\Desktop\Github Projects\excelasaph_rl_summative"
$RenderDir = "$ProjectRoot\3d-render"

# Check prerequisites
Write-Host "`n" @Cyan
Write-Host "Checking prerequisites..." @Cyan

$HasPython = python --version 2>&1
if ($HasPython -match "Python") {
    Write-Host "  ✓ Python: $HasPython" @Green
} else {
    Write-Host "  ✗ Python not found" @Red
    exit 1
}

$HasNode = node --version 2>&1
if ($HasNode) {
    Write-Host "  ✓ Node.js: $HasNode" @Green
} else {
    Write-Host "  ✗ Node.js not found" @Red
    exit 1
}

$HasNpm = npm --version 2>&1
if ($HasNpm) {
    Write-Host "  ✓ npm: $HasNpm" @Green
} else {
    Write-Host "  ✗ npm not found" @Red
    exit 1
}

# Check ports
Write-Host "`nChecking ports..." @Cyan
try {
    $Port5000 = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
    if ($Port5000) {
        Write-Host "  ⚠ Port 5000 already in use" @Yellow
    } else {
        Write-Host "  ✓ Port 5000 available" @Green
    }
} catch {}

try {
    $Port5173 = Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue
    if ($Port5173) {
        Write-Host "  ⚠ Port 5173 already in use" @Yellow
    } else {
        Write-Host "  ✓ Port 5173 available" @Green
    }
} catch {}

# Check dependencies
Write-Host "`nChecking dependencies..." @Cyan
if (Test-Path "$ProjectRoot\requirements.txt") {
    Write-Host "  ✓ Backend requirements.txt found" @Green
} else {
    Write-Host "  ✗ requirements.txt not found" @Red
    exit 1
}

if (Test-Path "$RenderDir\package.json") {
    Write-Host "  ✓ Frontend package.json found" @Green
} else {
    Write-Host "  ✗ package.json not found" @Red
    exit 1
}

# Install frontend dependencies if needed
Write-Host "`nChecking frontend dependencies..." @Cyan
if (!(Test-Path "$RenderDir\node_modules")) {
    Write-Host "  Installing npm packages..." @Yellow
    Push-Location $RenderDir
    npm install
    Pop-Location
    Write-Host "  ✓ npm packages installed" @Green
} else {
    Write-Host "  ✓ npm packages already installed" @Green
}

# Start services
Write-Host "`n" @Cyan
Write-Host "╔════════════════════════════════════════════════════════════════╗" @Cyan
Write-Host "║  Starting System Components...                                 ║" @Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" @Cyan

# Start Flask
Write-Host "`nStarting Flask Backend (Terminal 1)..." @Cyan
Write-Host "  Command: python flask_api.py" @Cyan
$FlaskProcess = Start-Process -NoNewWindow -PassThru -FilePath python `
    -ArgumentList "flask_api.py" `
    -WorkingDirectory $ProjectRoot `
    -EnvironmentVariable @{ PYTHONUNBUFFERED = "1" }

Write-Host "  ✓ Flask started (PID: $($FlaskProcess.Id))" @Green

# Wait for Flask to start
Write-Host "`n  Waiting for Flask to initialize..." @Yellow
Start-Sleep -Seconds 3

# Check Flask health
$FlaskHealth = $null
for ($i = 0; $i -lt 10; $i++) {
    try {
        $FlaskHealth = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($FlaskHealth.StatusCode -eq 200) {
            Write-Host "  ✓ Flask is responding" @Green
            break
        }
    } catch {}
    Start-Sleep -Seconds 1
}

if (!$FlaskHealth) {
    Write-Host "  ⚠ Flask may still be starting... continuing anyway" @Yellow
}

# Start React
Write-Host "`nStarting React Frontend (Terminal 2)..." @Cyan
Write-Host "  Command: npm run dev" @Cyan
$ReactProcess = Start-Process -NoNewWindow -PassThru -FilePath npm `
    -ArgumentList "run", "dev" `
    -WorkingDirectory $RenderDir

Write-Host "  ✓ React started (PID: $($ReactProcess.Id))" @Green
Write-Host "  Waiting for React to compile..." @Yellow
Start-Sleep -Seconds 5

# Summary
Write-Host "`n" @Cyan
Write-Host "╔════════════════════════════════════════════════════════════════╗" @Cyan
Write-Host "║  System Started Successfully!                                 ║" @Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" @Cyan

Write-Host "`nAccess Points:" @Green
Write-Host "  Flask API:     http://localhost:5000" @Cyan
Write-Host "  React App:     http://localhost:5173" @Cyan
Write-Host "  WebSocket:     ws://localhost:5000/socket.io" @Cyan

Write-Host "`nProcesses:" @Green
Write-Host "  Flask PID:     $($FlaskProcess.Id)" @Cyan
Write-Host "  React PID:     $($ReactProcess.Id)" @Cyan

Write-Host "`nNext Steps:" @Green
Write-Host "  1. Open browser: http://localhost:5173" @Cyan
Write-Host "  2. Press F12 (open console)" @Cyan
Write-Host "  3. Paste in console:" @Cyan
Write-Host "     socket.emit('start-episode')" @Cyan
Write-Host "     socket.emit('step', {})" @Cyan
Write-Host "" @Cyan
Write-Host "  OR run tests:" @Cyan
Write-Host "     python test_integration.py" @Cyan
Write-Host "     runAllFrontendTests()  (in browser console)" @Cyan

if (!$SkipTests) {
    Write-Host "`n" @Cyan
    Write-Host "Run backend tests? (Y/n)" @Yellow
    $Response = Read-Host
    
    if ($Response -ne "n") {
        Write-Host "`nStarting backend integration tests..." @Cyan
        Start-Sleep -Seconds 1
        & python test_integration.py -WorkingDirectory $ProjectRoot
    }
}

Write-Host "`n" @Green
Write-Host "System is running! You can now:" @Green
Write-Host "  • Open http://localhost:5173 in browser" @Green
Write-Host "  • Use browser console to control episodes" @Green
Watch the 3D visualization in real-time!" @Green
Write-Host ""

if (!$DontWait) {
    Write-Host "Press any key to stop all services..." @Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    Write-Host "`nStopping services..." @Yellow
    
    if ($FlaskProcess) {
        Stop-Process -Id $FlaskProcess.Id -ErrorAction SilentlyContinue
        Write-Host "  ✓ Flask stopped" @Green
    }
    
    if ($ReactProcess) {
        Stop-Process -Id $ReactProcess.Id -ErrorAction SilentlyContinue
        Write-Host "  ✓ React stopped" @Green
    }
    
    Write-Host "`nSystem shutdown complete." @Green
}

Write-Host ""
