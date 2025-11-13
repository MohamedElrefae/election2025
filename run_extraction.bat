@echo off
echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Starting PDF extraction...
python extract_motobus.py

echo.
echo Extraction complete! Check the output folder for results.
pause
