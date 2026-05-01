#!/bin/bash
# Unix/Mac startup script for Flask Sentiment Analysis App

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  DistilBERT Sentiment Analysis - Flask Web Server         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python3 is not installed"
    exit 1
fi

# Check if model exists
if [ ! -d "models/best_model" ]; then
    echo "❌ ERROR: Trained model not found at models/best_model"
    echo ""
    echo "Please train the model first:"
    echo "  python3 train.py"
    echo ""
    exit 1
fi

# Check if Flask is installed
python3 -c "import flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ ERROR: Flask is not installed"
    echo ""
    echo "Installing Flask and dependencies..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo "✓ All checks passed"
echo ""
echo "Starting Flask server..."
echo "🌐 Open your browser at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py
