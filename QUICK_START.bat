@echo off
title Egypt 2025 Election PDF Extraction - Quick Start

echo.
echo ===============================================================================
echo                Egypt 2025 Election PDF Extraction - Quick Start
echo ===============================================================================
echo.
echo This script will:
echo   1. Setup the environment and install dependencies
echo   2. Run the complete PDF extraction pipeline
echo   3. Generate CSV files and database-ready data
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python is available. Proceeding with setup...
echo.

REM Step 1: Setup environment
echo ===============================================================================
echo STEP 1: Setting up environment and installing dependencies...
echo ===============================================================================
echo.

python setup_extraction_environment.py
if errorlevel 1 (
    echo.
    echo ERROR: Environment setup failed!
    echo Please check the error messages above and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo Environment setup completed successfully!
echo.

REM Step 2: Check for PDF file
echo ===============================================================================
echo STEP 2: Checking for PDF file...
echo ===============================================================================
echo.

if not exist "motobus .pdf" (
    echo ERROR: PDF file "motobus .pdf" not found!
    echo.
    echo Please ensure the PDF file is in the current directory.
    echo The filename should be exactly: motobus .pdf
    echo ^(note the space in the filename^)
    echo.
    pause
    exit /b 1
)

echo PDF file found: motobus .pdf
echo.

REM Step 3: Run extraction
echo ===============================================================================
echo STEP 3: Running PDF extraction pipeline...
echo ===============================================================================
echo.

python run_complete_extraction.py
if errorlevel 1 (
    echo.
    echo ERROR: Extraction pipeline failed!
    echo Please check the error messages above.
    echo.
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo                            EXTRACTION COMPLETED!
echo ===============================================================================
echo.
echo Your Egypt 2025 election data has been successfully extracted!
echo.
echo Generated files:
echo   - output\locations_table.csv     ^(Polling stations data^)
echo   - output\voters_table.csv        ^(Individual voters data^)
echo   - output\election_data.json      ^(Complete dataset in JSON^)
echo   - output\pipeline_final_report.md ^(Comprehensive report^)
echo.
echo Next steps:
echo   1. Review the generated reports in the 'output' directory
echo   2. Import the CSV files into your preferred database or analytics tool
echo   3. Configure Supabase credentials for automatic database transfer ^(optional^)
echo.
echo For database transfer:
echo   - Copy supabase_config.json.sample to supabase_config.json
echo   - Fill in your Supabase URL and API key
echo   - Run the extraction again for automatic database transfer
echo.

pause