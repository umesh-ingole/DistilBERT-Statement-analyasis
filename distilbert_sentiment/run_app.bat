@echo off
REM Windows startup script for Flask Sentiment Analysis App

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║  DistilBERT Sentiment Analysis - Flask Web Server         ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python or add it to your PATH
    pause
    exit /b 1
)

REM Check if model exists
if not exist "models\best_model" (
    echo ❌ ERROR: Trained model not found at models\best_model
    echo.
    echo Please train the model first:
    echo   python train.py
    echo.
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Flask is not installed
    echo.
    echo Installing Flask and dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo ✓ All checks passed
echo.
echo Starting Flask server...
echo 🌐 Open your browser at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
