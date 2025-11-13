@echo off
echo ========================================
echo Starting Election Data Manager WebApp
echo ========================================
echo.

cd /d "%~dp0"

if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting development server...
echo.
echo The app will open at: http://localhost:3000
echo.
call npm run dev

pause
