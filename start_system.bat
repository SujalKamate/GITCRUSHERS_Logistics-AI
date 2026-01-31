@echo off
echo Starting Logistics AI Control System...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements_production.txt

REM Run system test
echo.
echo Running system tests...
python test_system.py

if errorlevel 1 (
    echo.
    echo System tests failed. Please check the configuration.
    pause
    exit /b 1
)

echo.
echo System tests passed! Starting services...
echo.

REM Start the API server
echo Starting API server on http://localhost:8000
echo Press Ctrl+C to stop
echo.

python -m uvicorn src.api.main:app --reload --port 8000

pause