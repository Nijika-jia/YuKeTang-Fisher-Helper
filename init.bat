@echo off
cd /d "%~dp0"

echo ==============================================
echo    Yuketang Helper Initializing...
echo ==============================================

echo.
echo [1/2] Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo WARNING: npm finished with warnings
)
cd ..

echo.
echo [2/2] Installing backend dependencies...
cd backend
call pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Backend install failed!
    pause
    exit /b 1
)
cd ..

echo.
echo ==============================================
echo Initialization completed!
echo Please run run.bat to start.
echo ==============================================

pause