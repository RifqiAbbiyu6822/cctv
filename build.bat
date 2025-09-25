@echo off
echo ========================================
echo    Building Car Counter YOLO App
echo ========================================
echo.

echo [1/4] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo Done.

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt
echo Done.

echo.
echo [3/4] Building executable with PyInstaller...
pyinstaller CarCounterYOLO.spec --clean --noconfirm
echo Done.

echo.
echo [4/4] Build completed!
echo.
echo Executable location: dist\CarCounterYOLO.exe
echo.
echo To run the app, double-click: dist\CarCounterYOLO.exe
echo.
pause
