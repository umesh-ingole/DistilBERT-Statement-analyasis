@echo off
REM Windows batch script for setting up training environment

echo.
echo ========================================
echo DistilBERT Training Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate venv
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo WARNING: pip upgrade had issues, continuing...
)

REM Install PyTorch CPU
echo Installing PyTorch (CPU version)...
pip install torch --index-url https://download.pytorch.org/whl/cpu
if errorlevel 1 (
    echo ERROR: Failed to install PyTorch
    pause
    exit /b 1
)

REM Install other dependencies
echo Installing other dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Verification
echo.
echo ========================================
echo Verifying Installation
echo ========================================
echo.

python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import transformers; print('Transformers:', transformers.__version__)"
python -c "from datasets import load_dataset; print('Datasets: OK')"
python -c "from sklearn.metrics import accuracy_score; print('Scikit-learn: OK')"
python -c "from accelerate import Accelerator; print('Accelerate: OK')"
python -c "import numpy; print('NumPy: OK')"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Virtual environment: venv
echo To activate: venv\Scripts\activate.bat
echo.
pause
