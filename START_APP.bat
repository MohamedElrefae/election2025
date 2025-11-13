@echo off
echo ========================================
echo Election 2025 - Web Application
echo ========================================
echo.
echo Starting the application...
echo.

cd webapp

if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting development server...
echo The app will open at: http://localhost:3000
echo.
call npm run dev

pause
