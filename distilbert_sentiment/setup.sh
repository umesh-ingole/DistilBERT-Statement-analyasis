#!/bin/bash

# macOS/Linux setup script for training environment

echo ""
echo "========================================"
echo "DistilBERT Training Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.8+"
    exit 1
fi

python3 --version

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create venv"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate venv"
    exit 1
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel

# Install PyTorch CPU
echo "Installing PyTorch (CPU version)..."
pip install torch --index-url https://download.pytorch.org/whl/cpu
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install PyTorch"
    exit 1
fi

# Install other dependencies
echo "Installing other dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi

# Verification
echo ""
echo "========================================"
echo "Verifying Installation"
echo "========================================"
echo ""

python -c "import torch; print('PyTorch:', torch.__version__)"
python -c "import transformers; print('Transformers:', transformers.__version__)"
python -c "from datasets import load_dataset; print('Datasets: OK')"
python -c "from sklearn.metrics import accuracy_score; print('Scikit-learn: OK')"
python -c "from accelerate import Accelerator; print('Accelerate: OK')"
python -c "import numpy; print('NumPy: OK')"

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Virtual environment: venv"
echo "To activate: source venv/bin/activate"
echo ""
