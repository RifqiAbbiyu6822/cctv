# PowerShell script untuk build Car Counter YOLO App
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Building Car Counter YOLO App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
Write-Host "Done." -ForegroundColor Green

Write-Host ""
Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "Done." -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Building executable with PyInstaller..." -ForegroundColor Yellow
pyinstaller CarCounterYOLO.spec --clean --noconfirm
Write-Host "Done." -ForegroundColor Green

Write-Host ""
Write-Host "[4/4] Build completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Executable location: dist\CarCounterYOLO.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the app, double-click: dist\CarCounterYOLO.exe" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"
